import json
from typing import List, Dict, Any

from groq import Groq

from backend.app.core.config import settings
from backend.app.models.schemas import (
    PresentationRequest,
    SlideContent,
    SlideType,
    AudienceLevel,
    PresentationStyle,
    Language,
)


class LLMService:
    """
    Service for interacting with Groq to generate
    high-quality, structured slide content.
    """

    def __init__(self):
        self.client = Groq(api_key=settings.GROQ_API_KEY)
        self.model = settings.GROQ_MODEL
        print(">>> USING GROQ MODEL:", settings.GROQ_MODEL)

    # ---------------------------
    # PUBLIC: main entry point
    # ---------------------------
    def generate_slide_content(
        self, request: PresentationRequest, rag_context: Dict[str, Any] | None = None
    ) -> List[SlideContent]:
        """
        Main entry point for generating slide content. Accepts an optional rag_context
        dict returned by the RAG service. This context will be inserted into the prompt
        to ground factual claims.
        """
        prompt = self._build_generation_prompt(request, rag_context=rag_context)

        print("[LLMService] Generated prompt preview (first 800 chars):")
        print(prompt[:800].replace("\n", " "))

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are an expert teacher and presentation designer. "
                            "You create clear, structured, engaging slide decks for students."
                        ),
                    },
                    {
                        "role": "user",
                        "content": prompt,
                    },
                ],
                temperature=0.6,
                max_tokens=8000,
            )

            raw_text = response.choices[0].message.content
            slides_dict = self._extract_and_parse_json(raw_text)

            if not slides_dict:
                return self._generate_template_slides(request)

            return self._parse_slides(slides_dict, request)

        except Exception as e:
            print(f"Error in generate_slide_content: {e}")
            return self._generate_template_slides(request)

    # ---------------------------
    # NEW IMPROVED PROMPT
    # ---------------------------
    def _build_generation_prompt(self, request: PresentationRequest, rag_context: Dict[str, Any] | None = None) -> str:
        """
        Build the LLM prompt. If rag_context is provided and contains 'context',
        include it as a 'REFERENCE MATERIALS' section. Limit size to prevent excessively long prompts.
        """
        audience_map = {
            AudienceLevel.ELEMENTARY: "children studying in grades 1–5",
            AudienceLevel.MIDDLE: "students in grades 6–8",
            AudienceLevel.HIGH: "class 9–12 students",
            AudienceLevel.COLLEGE: "undergraduate learners",
            AudienceLevel.PROFESSIONAL: "industry professionals",
        }

        style_map = {
            PresentationStyle.ACADEMIC: "structured, clear, textbook-oriented",
            PresentationStyle.STORYTELLING: "narrative with relatable scenarios and examples",
            PresentationStyle.INTERACTIVE: "engaging, question-based, activity-driven",
            PresentationStyle.TECHNICAL: "precise, systematic, process-focused",
            PresentationStyle.VISUAL: "minimal text, diagram-friendly, visual-oriented",
        }

        audience_desc = audience_map.get(request.audience_type, "students")
        style_desc = style_map.get(request.presentation_style, "clear and structured")

        language = request.language.value
        num_slides = request.num_slides
        include_quiz = request.include_quiz

        # Calculate distribution to ensure EXACT count
        # Fixed: Title (1) + Intro (1) + Examples (1) + Summary (1) = 4
        fixed_count = 4
        if include_quiz:
            fixed_count += 1
        
        core_slides = max(1, num_slides - fixed_count)

        # Build RAG section if available
        rag_section = ""
        if rag_context and rag_context.get("has_context"):
            # Truncate to ~3000 chars to stay within token budget
            raw_context = rag_context.get("context", "")
            truncated = raw_context[:3000]
            rag_section = f"""
REFERENCE MATERIALS FROM KNOWLEDGE BASE (USE WHEN RELEVANT):
{truncated}

Please use these reference materials to ground factual claims, and cite the source name and page number in parentheses when you use specific facts.
"""
        else:
            rag_section = ""  # no context available

        prompt = f"""
You are an expert educator who designs high-quality presentation slides.

TASK:
Generate a JSON array of EXACTLY {num_slides} slides about: "{request.topic}".
IMPORTANT: The Title, Introduction, Quiz, and Summary slides ARE INCLUDED in this total count of {num_slides}. Do NOT generate extra slides.

REQUIREMENTS:
- Write all content in {language}.
- Each slide must have **4–6 rich bullet points** (not short phrases).
- Bullets must be explanatory, clear, and teaching-oriented.
- Every slide must include one relevant short English "image_query".
- Speaker notes must be **comprehensive and detailed (approx. 100 words)**. They should elaborate on the slide content, provide additional context or examples, and be written in a conversational tone suitable for a presenter.

{rag_section}

SLIDE STRUCTURE (Distribution within the {num_slides} slides):
1. TITLE slide (1 slide)
2. Overview / introduction (1 slide)
3. Core concept slides ({core_slides} slides)
4. Real-world examples / applications (1 slide)
5. {"Quiz slide (1 slide)" if include_quiz else "Optional quiz slide only if meaningful (0 slides)"}
6. Summary slide (1 slide)

ALLOWED SLIDE TYPES:
"title", "content", "summary", "quiz", "image_heavy"

FORMAT (VERY IMPORTANT):
Return ONLY this JSON (no markdown fences):

{{
  "slides": [
    {{
      "type": "content",
      "title": "...",
      "subtitle": null,
      "content": ["bullet 1", "bullet 2", "bullet 3", "bullet 4"],
      "image_query": "educational photo of ...",
      "speaker_notes": "Detailed paragraph explaining the slide concepts for the presenter, adding context and examples."
    }}
  ]
}}

Make the content deeply informative, well-structured, and age-appropriate for {audience_desc}.
"""
        return prompt.strip()
    # ---------------------------
    # JSON HANDLING
    # ---------------------------
    def _extract_and_parse_json(self, text: str) -> Dict[str, Any] | None:
        if not text:
            return None

        if "```" in text:
            parts = text.split("```")
            candidate = None
            for part in parts:
                if "{" in part:
                    candidate = part
                    break
            text = candidate or text

        text = text.strip()
        if text.lower().startswith("json"):
            text = text[4:].strip()

        start = text.find("{")
        end = text.rfind("}")

        if start == -1 or end == -1 or end <= start:
            return None

        json_str = text[start: end + 1]

        try:
            return json.loads(json_str)
        except Exception as e:
            print(f"JSON parse error: {e}")
            print("RAW TEXT:", text[:400])
            return None

    # ---------------------------
    # SLIDE PARSING
    # ---------------------------
    def _parse_slides(
        self, slides_data: Dict[str, Any], request: PresentationRequest
    ) -> List[SlideContent]:

        raw_slides = slides_data.get("slides", [])
        slides: List[SlideContent] = []

        if not isinstance(raw_slides, list):
            return self._generate_template_slides(request)

        for slide_data in raw_slides:

            slide_type_str = str(slide_data.get("type", "content")).lower()
            try:
                slide_type = SlideType(slide_type_str)
            except:
                slide_type = SlideType.CONTENT

            content_list = []
            content = slide_data.get("content", [])

            if isinstance(content, str):
                content_list = [content]
            elif isinstance(content, list):
                content_list = [str(item) for item in content if item]

            notes = slide_data.get("speaker_notes")
            if not request.speaker_notes:
                notes = None

            slides.append(
                SlideContent(
                    type=slide_type,
                    title=str(slide_data.get("title", request.topic)),
                    subtitle=slide_data.get("subtitle"),
                    content=content_list,
                    image_query=slide_data.get("image_query") or request.topic,
                    image_url=None,
                    speaker_notes=notes,
                    layout="default",
                )
            )

        # ---------------------------
        # FORCE EXACT SLIDE COUNT
        # ---------------------------
        target_count = request.num_slides
        current_count = len(slides)

        # Case 1: Too many slides -> Truncate
        if current_count > target_count:
            print(f"[LLMService] Truncating slides from {current_count} to {target_count}")
            slides = slides[:target_count]

        # Case 2: Too few slides -> Pad
        elif current_count < target_count:
            needed = target_count - current_count
            print(f"[LLMService] Padding {needed} slides to reach {target_count}")
            
            # Insert before the last slide (usually Summary) if possible, else append
            insert_idx = max(0, len(slides) - 1)
            
            for i in range(needed):
                # Dynamic templates to make padding look less repetitive
                templates = [
                    {
                        "title": f"Real-World Application: {request.topic}",
                        "subtitle": "Practical Implementation Case Study",
                        "content": [
                            "How these concepts apply to modern industry.",
                            "Impact on daily life and technology.",
                            "Solving real problems using this knowledge.",
                            "Case study example in current field."
                        ],
                        "query": f"real world application of {request.topic}"
                    },
                    {
                        "title": f"Future Trends in {request.topic}",
                        "subtitle": "Looking Ahead",
                        "content": [
                            "Emerging technologies and innovations.",
                            "How this field is evolving rapidly.",
                            "Future challenges and opportunities.",
                            "The next decade of development."
                        ],
                        "query": f"future technology {request.topic}"
                    },
                    {
                        "title": f"Global Impact of {request.topic}",
                        "subtitle": "Societal Perspective",
                        "content": [
                            "Influence on global standards and practices.",
                            "Economic and environmental implications.",
                            "Cross-cultural relevance and adoption.",
                            "Why this matters to the wider world."
                        ],
                        "query": f"global impact of {request.topic}"
                    }
                ]
                
                # Cycle through templates
                tmpl = templates[i % len(templates)]

                new_slide = SlideContent(
                    type=SlideType.CONTENT,
                    title=tmpl["title"],
                    subtitle=tmpl["subtitle"],
                    content=tmpl["content"],
                    image_query=tmpl["query"],
                    image_url=None,
                    speaker_notes=f"This slide expands on the practical applications and implications of {request.topic}, providing a broader context for the audience to understand its real-value.",
                    layout="default",
                )
                slides.insert(insert_idx, new_slide)

        return slides

    # ---------------------------
    # SIMPLE TEMPLATE FALLBACK
    # ---------------------------
    def _generate_template_slides(self, request: PresentationRequest) -> List[SlideContent]:

        slides: List[SlideContent] = []

        slides.append(
            SlideContent(
                type=SlideType.TITLE,
                title=request.topic,
                subtitle=None,
                content=[],
                image_query=request.topic,
                image_url=None,
                speaker_notes=None,
                layout="default",
            )
        )

        for i in range(1, request.num_slides):
            slides.append(
                SlideContent(
                    type=SlideType.CONTENT,
                    title=f"{request.topic} – Key Idea {i}",
                    subtitle=None,
                    content=[
                        f"Important concept {i}",
                        f"Explanation {i}",
                        f"Example {i}",
                    ],
                    image_query=request.topic,
                    image_url=None,
                    speaker_notes=None,
                    layout="default",
                )
            )

        return slides


llm_service = LLMService()
