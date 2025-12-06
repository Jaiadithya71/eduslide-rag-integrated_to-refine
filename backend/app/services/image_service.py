import hashlib
import time
from typing import Optional, List, Set

import requests
from backend.app.core.config import settings

# OpenAI is optional – hybrid mode works even if it's missing
try:
    from openai import OpenAI  # type: ignore
except ImportError:  # pragma: no cover - optional dependency
    OpenAI = None

# Gemini is optional - for smart search query generation
try:
    import google.generativeai as genai
except ImportError:
    genai = None


class ImageService:
    """
    Hybrid Image Engine

    - Uses OpenAI for clean educational diagrams when helpful.
    - Uses Freepik for realistic photos, vectors, and illustrations.
    - Filters out people / classroom / ADHD stock images.
    - Avoids repeating the same URL across slides.
    """

    def __init__(self) -> None:
        # Freepik API
        self.api_key = getattr(settings, "FREEPIK_API_KEY", None)
        self.base_url = "https://api.freepik.com/v1"

        # Gemini AI (optional - for smart search queries)
        self.gemini_api_key = getattr(settings, "GEMINI_API_KEY", None)
        self._gemini_model = None
        if genai is not None and self.gemini_api_key:
            try:
                genai.configure(api_key=self.gemini_api_key)
                self._gemini_model = genai.GenerativeModel('gemini-2.5-flash')
                print(f"[Gemini] Initialized for smart search queries")
            except Exception as e:
                print(f"[Gemini] Failed to init: {e}")
                self._gemini_model = None

        # OpenAI (optional)
        self.openai_api_key = getattr(settings, "OPENAI_API_KEY", None)
        self.openai_image_model = getattr(
            settings, "OPENAI_IMAGE_MODEL", "gpt-image-1"
        )
        self.image_strategy = getattr(
            settings, "IMAGE_STRATEGY", "hybrid"
        ).lower()  # "hybrid" / "freepik" / "openai"

        self._openai_client = None
        if OpenAI is not None and self.openai_api_key:
            try:
                self._openai_client = OpenAI(api_key=self.openai_api_key)
            except Exception as e:
                print(f"[OpenAI] Failed to init image client: {e}")
                self._openai_client = None

    # ------------------------------------------------------------------
    # PUBLIC HYBRID ENTRY
    # ------------------------------------------------------------------
    def get_hybrid_image_for_slide(
        self,
        topic: str,
        slide,
        slide_index: int,
        language,
        presentation_style,
        used_urls: Set[str],
    ) -> Optional[str]:
        """
        Decide the best image provider for this slide and return a URL.
        Priority: Freepik Stock (FREE, content-aware) > OpenAI > Placeholder
        
        Note: AI generation is available but disabled by default (costs money).
        To enable: uncomment the AI generation section below.
        """

        topic_text = (topic or "").strip()
        style_val = getattr(presentation_style, "value", str(presentation_style)).lower()
        lang_val = getattr(language, "value", str(language)).lower()
        title = (slide.title or "").strip()
        content = getattr(slide, "content", []) or []

        needs_diagram = self._needs_diagram(topic_text, title, style_val)

        # Helper to avoid repetition
        def remember(url: Optional[str]) -> Optional[str]:
            if url and url not in used_urls:
                used_urls.add(url)
            return url

        # ============================================================
        # DISABLED: Freepik AI Generation (costs ~$0.05 per image)
        # Uncomment below to enable AI-generated custom images
        # ============================================================
        # if self.image_strategy in {"hybrid", "freepik", "ai"}:
        #     print(f"[ImageService] Trying Freepik AI generation for slide: {title}")
        #     ai_url = self._generate_freepik_ai_image(
        #         topic=topic_text,
        #         slide_title=title,
        #         slide_content=content,
        #         slide_type=getattr(slide, "type", None),
        #         language=lang_val,
        #     )
        #     if ai_url and ai_url not in used_urls:
        #         print(f"[ImageService] ✓ Using Freepik AI generated image")
        #         return remember(ai_url)

        # Strategy 1: Freepik Stock Search (FREE - uses slide content for better queries)
        if self.image_strategy in {"hybrid", "freepik"}:
            freepik_url = self._search_freepik_for_slide(
                topic=topic_text,
                slide=slide,
                slide_index=slide_index,
                used_urls=used_urls,
            )
            if freepik_url:
                print(f"[ImageService] ✓ Using Freepik stock image (content-aware)")
                return remember(freepik_url)

        # Strategy 2: OpenAI diagrams (if available)
        if self._openai_client and self.image_strategy in {"hybrid", "openai"}:
            if needs_diagram:
                ai_url = self._generate_openai_diagram(
                    topic=topic_text,
                    slide_title=title,
                    slide_type=getattr(slide, "type", None),
                    language=lang_val,
                )
                if ai_url and ai_url not in used_urls:
                    print(f"[ImageService] ✓ Using OpenAI diagram")
                    return remember(ai_url)

        # Final fallback: placeholder
        print(f"[ImageService] Using placeholder image")
        return self._get_placeholder_image(topic_text or title or "education")

    # ------------------------------------------------------------------
    # DECISION: does this slide really need a diagram?
    # ------------------------------------------------------------------
    def _needs_diagram(self, topic: str, title: str, style_val: str) -> bool:
        text = f"{topic} {title}".lower()

        # Obvious STEM / diagram-heavy topics
        diagram_keywords = [
            "regression",
            "linear regression",
            "logistic regression",
            "machine learning",
            "neural network",
            "algorithm",
            "data structure",
            "statistics",
            "probability",
            "graph theory",
            "function",
            "equation",
            "calculus",
            "derivative",
            "integral",
            "matrix",
            "vector",
            "physics",
            "chemistry",
            "digestive",
            "stomach",
            "intestine",
            "esophagus",
            "heart",
            "circulatory",
            "respiratory",
            "lungs",
            "brain",
            "nervous system",
            "kidney",
            "liver",
            "orbit",
            "solar system",
            "circuit",
            "transistor",
            "os",
            "operating system",
            "computer architecture",
        ]

        if any(k in text for k in diagram_keywords):
            return True

        # Strong technical styles also benefit from diagrams
        if any(tag in style_val for tag in ["technical", "deep_dive", "technical_deep_dive"]):
            return True

        return False

    # ------------------------------------------------------------------
    # OPENAI IMAGE GENERATION
    # ------------------------------------------------------------------
    def _generate_openai_diagram(
        self,
        topic: str,
        slide_title: str,
        slide_type,
        language: str,
    ) -> Optional[str]:
        """
        Generate a simple educational diagram via OpenAI images.
        Returns an image URL if successful.
        """
        if not self._openai_client:
            return None

        base = topic or slide_title or "educational concept"
        base = base.strip()

        # Hint based on slide type
        slide_type_name = getattr(slide_type, "value", str(slide_type) or "").lower()
        type_hint = ""
        if "title" in slide_type_name:
            type_hint = "overview concept illustration"
        elif "summary" in slide_type_name:
            type_hint = "summary infographic with simple visual metaphor"
        elif "quiz" in slide_type_name:
            type_hint = "clean quiz iconography without text"
        else:
            type_hint = "process or relationship diagram"

        prompt = (
            f"Flat, clean educational diagram about '{base}'. "
            f"Show the key idea visually, with arrows or simple shapes. "
            f"No human faces, no classroom photos. "
            f"White or light background, high contrast, suitable for a PowerPoint slide. "
            f"Style: minimal, vector-like illustration. {type_hint}."
        )

        try:
            result = self._openai_client.images.generate(
                model=self.openai_image_model,
                prompt=prompt,
                size="1024x1024",
                n=1,
            )
            data = getattr(result, "data", None) or []
            if not data:
                return None

            item = data[0]
            # Newer OpenAI clients expose 'url'
            url = getattr(item, "url", None)
            if not url:
                # some clients use dict-like objects
                url = getattr(item, "get", lambda *_a, **_k: None)("url")
            return url
        except Exception as e:
            print(f"[OpenAI] Image generation failed: {e}")
            return None

    # ------------------------------------------------------------------
    # FREEPIK MYSTIC AI IMAGE GENERATION
    # ------------------------------------------------------------------
    def _generate_freepik_ai_image(
        self,
        topic: str,
        slide_title: str,
        slide_content: List[str],
        slide_type,
        language: str,
    ) -> Optional[str]:
        """
        Generate a custom educational image using Freepik Mystic AI.
        Returns an image URL if successful.
        """
        if not self.api_key or self.api_key == "your_freepik_api_key_here":
            return None

        # Build prompt from slide content
        prompt = self._build_ai_image_prompt(
            topic=topic,
            slide_title=slide_title,
            slide_content=slide_content,
            slide_type=slide_type
        )

        print(f"[Freepik AI] Generating image with prompt: {prompt[:100]}...")

        try:
            # Create generation task
            url = f"{self.base_url}/ai/mystic"
            headers = {
                "x-freepik-api-key": self.api_key,
                "Content-Type": "application/json"
            }
            payload = {
                "prompt": prompt,
                "resolution": "2k",
                "aspect_ratio": "landscape_16_9",
                "model": "realism",
                "filter_nsfw": True
            }

            response = requests.post(url, headers=headers, json=payload, timeout=15)
            response.raise_for_status()
            data = response.json()

            task_id = data.get("data", {}).get("task_id")
            if not task_id:
                print("[Freepik AI] No task_id returned")
                return None

            print(f"[Freepik AI] Task created: {task_id}, polling for completion...")

            # Poll for completion (max 30 seconds)
            max_attempts = 15
            poll_interval = 2  # seconds

            for attempt in range(max_attempts):
                time.sleep(poll_interval)

                status_url = f"{self.base_url}/ai/mystic/{task_id}"
                status_resp = requests.get(status_url, headers=headers, timeout=10)
                status_resp.raise_for_status()
                status_data = status_resp.json()

                task_status = status_data.get("data", {}).get("status")
                
                if task_status == "COMPLETED":
                    generated = status_data.get("data", {}).get("generated", [])
                    if generated and len(generated) > 0:
                        image_url = generated[0].get("url")
                        print(f"[Freepik AI] ✓ Image generated: {image_url[:80]}...")
                        return image_url
                    else:
                        print("[Freepik AI] Task completed but no images generated")
                        return None
                
                elif task_status == "FAILED":
                    print(f"[Freepik AI] Task failed")
                    return None
                
                elif task_status == "IN_PROGRESS":
                    print(f"[Freepik AI] Still generating... ({attempt + 1}/{max_attempts})")
                    continue
                
                else:
                    print(f"[Freepik AI] Unknown status: {task_status}")

            print("[Freepik AI] Timeout waiting for image generation")
            return None

        except Exception as e:
            print(f"[Freepik AI] Error: {e}")
            return None

    def _build_ai_image_prompt(
        self,
        topic: str,
        slide_title: str,
        slide_content: List[str],
        slide_type
    ) -> str:
        """
        Build a detailed prompt for AI image generation from slide content.
        """
        # Start with slide title
        base = slide_title or topic or "educational concept"
        
        # Add context from bullet points (first 2-3)
        if slide_content and isinstance(slide_content, list):
            content_text = " ".join(slide_content[:3])
            # Limit length
            if len(content_text) > 150:
                content_text = content_text[:150]
            base = f"{base}. {content_text}"
        
        # Style directives for educational content
        style = (
            "Create a clean educational illustration or diagram. "
            "Use simple, clear visuals with labels if needed. "
            "No people, no text overlays, no classroom photos. "
            "White or light background, high contrast. "
            "Suitable for a PowerPoint presentation slide. "
            "Professional, modern, vector-style illustration."
        )
        
        # Combine
        prompt = f"{base} {style}"
        
        # Limit total prompt length
        if len(prompt) > 500:
            prompt = prompt[:500]
        
        return prompt

    # ------------------------------------------------------------------
    # FREEPIK SEARCH + RANKING
    # ------------------------------------------------------------------
    def _search_freepik_for_slide(
        self,
        topic: str,
        slide,
        slide_index: int,
        used_urls: Set[str],
    ) -> Optional[str]:
        """
        Search Freepik with a smart query, rank images, avoid bad ones and repeats.
        """
        query = self._build_freepik_query(topic, slide)

        if not self.api_key or self.api_key == "your_freepik_api_key_here":
            # No key – fallback to placeholder
            return self._get_placeholder_image(query or topic)

        try:
            url = f"{self.base_url}/resources"
            params = {
                "term": query,
                "limit": 20,
                "order": "relevance",
            }
            headers = {
                "x-freepik-api-key": self.api_key,
                "Accept-Language": "en-US"
            }

            resp = requests.get(url, params=params, headers=headers, timeout=10)
            resp.raise_for_status()
            data = resp.json()

            resources: List[dict] = data.get("data") or []
            if not resources:
                return None

            primary_hint = self._extract_primary_keyword(query or topic)
            return self._pick_best_freepik_resource(
                resources=resources,
                primary_hint=primary_hint,
                avoid_urls=used_urls,
                slide_index=slide_index,
            )

        except Exception as e:
            print(f"[Freepik] Error for query '{query}': {e}")
            return None

    def _build_freepik_query(self, topic: str, slide) -> str:
        """
        Build search query using Gemini AI (if available) or fallback to manual extraction.
        Gemini analyzes slide content and generates optimal search queries.
        """
        topic = (topic or "").strip()
        title = (slide.title or "").strip()
        content = getattr(slide, "content", []) or []
        
        # Try Gemini first for AI-powered query generation
        if self._gemini_model and content:
            try:
                # Build MAXIMUM context prompt for Gemini
                # Include ALL content, not just first 3
                content_text = "\n".join(f"- {c}" for c in content)
                
                # Detect if this is a real-world application slide
                is_application_slide = any(keyword in title.lower() or keyword in content_text.lower() 
                                          for keyword in ["application", "real-world", "practical", "uses", "examples", "daily life", "industry", "agriculture"])
                
                if is_application_slide:
                    # Special prompt for real-world applications
                    prompt = f"""You are an expert at finding REALISTIC PHOTOS for educational presentations about real-world applications.

PRESENTATION TOPIC: {topic}
SLIDE TITLE: {title}

COMPLETE SLIDE CONTENT:
{content_text}

This slide is about REAL-WORLD APPLICATIONS and PRACTICAL EXAMPLES.

TASK: Generate a search query for REALISTIC PHOTOS (not diagrams) showing practical applications.

REQUIREMENTS:
1. Focus on REAL-WORLD scenarios, activities, or industries mentioned
2. Specify the SETTING or CONTEXT (e.g., "farm", "factory", "household", "city")
3. Include HUMAN ACTIVITIES if relevant (e.g., "farmer irrigating", "engineer testing")
4. Use terms like "realistic", "professional", "real", "actual" to get photos not diagrams
5. Maximum 15 words
6. DO NOT include "diagram" or "illustration" - we want REAL PHOTOS

OUTPUT: Only the search query, nothing else.

Search Query:"""
                else:
                    # Standard prompt for educational diagrams
                    prompt = f"""You are an expert at finding the PERFECT educational image for presentations.

PRESENTATION TOPIC: {topic}
SLIDE TITLE: {title}

COMPLETE SLIDE CONTENT:
{content_text}

TASK: Analyze this slide deeply and generate the most specific search query possible.

ANALYSIS REQUIREMENTS:
1. What is the PRIMARY visual concept this slide is explaining?
2. What specific structures, processes, or components should be shown?
3. What perspective or view would be most educational (cross-section, close-up, overview, cycle, flow)?
4. What are the KEY TERMS that differentiate this from other slides on the same topic?

SEARCH QUERY REQUIREMENTS:
- Maximum 15 words
- Include SPECIFIC scientific/technical terms from the content
- Specify the TYPE of diagram needed (e.g., "cross-section", "flowchart", "cycle diagram", "labeled anatomy")
- Focus on UNIQUE aspects that make this slide different from others
- Use precise terminology that will find a DIFFERENT image than other slides

OUTPUT: Only the search query, nothing else.

Search Query:"""
                
                response = self._gemini_model.generate_content(prompt)
                query = response.text.strip()
                
                # Clean up query - remove quotes if Gemini added them
                query = query.strip('"\'')
                
                # Add diagram hint ONLY for non-application slides
                if not is_application_slide and len(query.split()) < 8 and "diagram" not in query.lower() and "illustration" not in query.lower():
                    query += " diagram"
                
                tag = "[Gemini APP]" if is_application_slide else "[Gemini MAX]"
                print(f"{tag} '{query}'")
                return query
                
            except Exception as e:
                print(f"[Gemini] Query generation failed: {e}, falling back to manual")
        
        # Fallback: Manual query building
        query_parts = []
        if topic:
            query_parts.append(topic)
        if title:
            query_parts.append(title)
        
        # Extract key phrases from content
        if content and isinstance(content, list):
            content_text = " ".join(content[:2])
            key_phrases = self._extract_key_phrases(content_text)
            if key_phrases:
                query_parts.extend(key_phrases[:2])
        
        query = " ".join(query_parts).strip()
        
        # Add diagram hint
        if "diagram" not in query.lower() and "illustration" not in query.lower():
            query += " diagram"
        
        # Limit length
        if len(query) > 150:
            query = query[:150].rsplit(" ", 1)[0]
        
        print(f"[Manual Query] '{query}'")
        return query
    
    def _extract_key_phrases(self, text: str) -> List[str]:
        """Extract key scientific phrases (2-3 words) from content."""
        if not text:
            return []
        
        text = text.lower()
        phrases = []
        
        # Common scientific phrases
        known_phrases = [
            "krebs cycle", "citric acid cycle", "electron transport",
            "aerobic respiration", "anaerobic respiration",
            "cellular respiration", "glycolysis process",
            "calvin cycle", "light reactions",
            "atp synthesis", "glucose breakdown",
            "mitochondrial matrix", "cell membrane",
            "photosynthesis process", "water cycle",
            "digestive system", "nervous system", "circulatory system",
            "dna replication", "protein synthesis",
            "solar system", "carbon dioxide", "oxygen"
        ]
        
        for phrase in known_phrases:
            if phrase in text:
                phrases.append(phrase)
        
        # If no phrases, get important words
        if not phrases:
            words = text.replace(",", "").replace(".", "").split()
            stop = {"the", "a", "an", "and", "or", "is", "are", "this", "that", "in", "on", "at", "to", "for", "of", "with"}
            important = [w.strip(".,;:!?") for w in words if len(w) > 5 and w not in stop]
            return important[:2]
        
        return phrases[:2]
    
    def _extract_keywords_from_content(self, text: str) -> List[str]:
        """
        Extract important keywords from slide content.
        Focuses on nouns and technical terms.
        """
        if not text:
            return []
        
        # Common stop words to filter out
        stop_words = {
            "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
            "of", "with", "by", "from", "is", "are", "was", "were", "be", "been",
            "have", "has", "had", "do", "does", "did", "will", "would", "should",
            "could", "may", "might", "can", "this", "that", "these", "those",
            "it", "its", "they", "their", "them", "we", "our", "you", "your"
        }
        
        # Split into words
        words = text.lower().replace(",", " ").replace(".", " ").split()
        
        # Filter and extract keywords
        keywords = []
        for word in words:
            # Remove punctuation
            word = word.strip(".,;:!?()[]{}\"'")
            
            # Skip if too short, is stop word, or already added
            if len(word) < 4 or word in stop_words or word in keywords:
                continue
            
            # Keep technical terms, scientific words, proper nouns
            if (word[0].isupper() or  # Capitalized (proper noun)
                len(word) > 8 or  # Long words (likely technical)
                any(char.isdigit() for char in word)):  # Contains numbers
                keywords.append(word)
        
        return keywords[:5]  # Return top 5

    def _pick_best_freepik_resource(
        self,
        resources: List[dict],
        primary_hint: Optional[str],
        avoid_urls: Set[str],
        slide_index: int,
    ) -> Optional[str]:
        """
        Score and pick the best Freepik resource with improved relevance matching.
        
        Scoring priorities:
        1. Content relevance (keywords match)
        2. Vector/diagram type
        3. Educational quality
        4. Avoid people/classroom photos
        """

        if not resources:
            return None

        person_words = [
            "person", "people", "man", "woman", "boy", "girl", "child", "children",
            "students", "student", "teacher", "portrait", "face", "selfie",
            "classroom", "class room", "meeting", "team", "group of people",
            "adhd", "mental", "psychology", "therapy", "counseling",
        ]

        diagram_keywords = [
            "diagram", "graph", "chart", "plot", "equation", "formula",
            "data", "analytics", "statistics", "regression", "anatomy",
            "organ", "medical", "biology", "microscope", "infographic",
            "illustration", "concept map", "x-ray", "vector", "educational",
            "process", "cycle", "system", "structure", "scheme"
        ]

        def is_persony(title: str) -> bool:
            return any(w in title for w in person_words)

        def has_diagram_word(title: str) -> bool:
            return any(w in title for w in diagram_keywords)

        def has_primary_hint(title: str) -> bool:
            return bool(primary_hint) and primary_hint in title

        def resource_url(resource: dict) -> Optional[str]:
            image_data = resource.get("image") or {}
            source = image_data.get("source") or {}
            return source.get("url")
        
        def count_keyword_matches(title: str, keywords: List[str]) -> int:
            """Count how many keywords from the query appear in the title"""
            if not keywords:
                return 0
            title_lower = title.lower()
            matches = sum(1 for kw in keywords if kw.lower() in title_lower)
            return matches

        # Extract keywords from primary_hint for matching
        query_keywords = []
        if primary_hint:
            query_keywords = [w.strip() for w in primary_hint.split() if len(w.strip()) > 3]

        scored = []
        for r in resources:
            url = resource_url(r)
            if not url:
                continue

            title = str(r.get("title", "")).lower()
            image_type = r.get("image", {}).get("type", "").lower()
            
            score = 0
            
            # PRIORITY 1: Keyword relevance (most important!)
            keyword_matches = count_keyword_matches(title, query_keywords)
            score += keyword_matches * 10  # 10 points per matching keyword
            
            # PRIORITY 2: Prefer vectors and illustrations
            if image_type == "vector":
                score += 8
            elif image_type == "illustration":
                score += 6
            
            # PRIORITY 3: Educational diagram indicators
            if has_diagram_word(title):
                score += 5
            
            # PRIORITY 4: Primary hint match
            if has_primary_hint(title):
                score += 7
            
            # PENALTY: Avoid people/classroom photos
            if is_persony(title):
                score -= 20  # Strong penalty
            
            # PENALTY: Avoid text-heavy and template images (Lorem Ipsum!)
            # Check both title and description for text indicators
            description = str(r.get("description", "")).lower()
            combined_text = title + " " + description
            text_indicators = [
                "lorem", "ipsum", "text", "label", "template", "mockup", 
                "placeholder", "sample", "typography", "font", "lettering",
                "editable", "customizable", "your text here", "add text"
            ]
            if any(indicator in combined_text for indicator in text_indicators):
                score -= 30  # VERY strong penalty!
            
            # PENALTY: Infographics often have lots of text
            if "infographic" in combined_text:
                score -= 15
            
            # PENALTY: Avoid images with "design", "layout" (often templates)
            if any(design in combined_text for design in ["design template", "layout", "brochure", "flyer", "poster design"]):
                score -= 20
                
            # BONUS: Landscape orientation (better for slides)
            orientation = r.get("image", {}).get("orientation", "")
            if orientation == "landscape":
                score += 2
            
            # BONUS: Popularity indicates quality
            stats = r.get("stats", {})
            downloads = stats.get("downloads", 0)
            likes = stats.get("likes", 0)
            if downloads > 5000:
                score += 3
            elif downloads > 1000:
                score += 2
            if likes > 100:
                score += 2
            elif likes > 50:
                score += 1

            scored.append((score, url, title))

        if not scored:
            return None

        # Sort by score (best first)
        scored.sort(key=lambda t: t[0], reverse=True)
        
        # Log top 3 for debugging
        print(f"[Freepik] Top 3 scored images:")
        for i, (s, u, t) in enumerate(scored[:3], 1):
            print(f"  {i}. Score: {s:3d} - {t[:60]}...")

        # Filter out already used URLs (STRICT - prefer variety)
        fresh = [(s, u, t) for (s, u, t) in scored if u not in avoid_urls]
        
        # If we have fresh images, use them. Otherwise, only reuse if score is very high
        if fresh:
            scored = fresh
        elif scored:
            # Only allow reuse if the best score is exceptional (>30)
            if scored[0][0] < 30:
                print(f"[Freepik] All images used, and best score too low ({scored[0][0]}). Skipping.")
                return None
            print(f"[Freepik] WARNING: Reusing image (score: {scored[0][0]})")

        # ALWAYS pick the highest scored image (no randomization)
        _, chosen_url, chosen_title = scored[0]
        print(f"[Freepik] Selected: {chosen_title[:60]}... (score: {scored[0][0]})")
        return chosen_url

    # ------------------------------------------------------------------
    # PRIMARY KEYWORD EXTRACTION
    # ------------------------------------------------------------------
    def _extract_primary_keyword(self, text: str) -> Optional[str]:
        text = (text or "").lower()
        tokens = [t for t in text.replace("/", " ").split() if t.isalpha()]

        stop = {
            "the",
            "and",
            "of",
            "for",
            "in",
            "to",
            "a",
            "an",
            "on",
            "with",
            "introduction",
            "overview",
            "diagram",
            "illustration",
            "education",
            "system",
            "process",
        }

        filtered = [t for t in tokens if t not in stop]
        if not filtered:
            return None

        filtered.sort(key=len, reverse=True)
        return filtered[0]

    # ------------------------------------------------------------------
    # MULTI-IMAGE FETCH (still available if needed)
    # ------------------------------------------------------------------
    def get_multiple_images(
        self,
        queries: List[str],
        orientation: str = "landscape",
    ) -> List[Optional[str]]:
        results: List[Optional[str]] = []
        for q in queries:
            # Use Freepik search here; hybrid is mainly per-slide
            url = self.search_image(q, orientation=orientation, per_page=10)
            results.append(url)
        return results

    # Simple direct search if you still need it elsewhere
    def search_image(
        self,
        query: str,
        orientation: str = "landscape",
        per_page: int = 1,
    ) -> Optional[str]:
        return self._search_freepik_for_slide(
            topic=query,
            slide=type("DummySlide", (), {"title": query, "image_query": ""})(),
            slide_index=0,
            used_urls=set(),
        )

    # ------------------------------------------------------------------
    # PLACEHOLDER / FALLBACK
    # ------------------------------------------------------------------
    def _get_placeholder_image(self, query: str) -> str:
        """
        Deterministic but varied placeholder image using a hash of the query.
        """
        base = (query or "lesson").strip().lower()
        digest = hashlib.sha256(base.encode("utf-8")).hexdigest()[:8]
        seed = f"{base}-{digest}"
        return f"https://picsum.photos/seed/{seed}/1600/900"

    # ------------------------------------------------------------------
    # EDUCATIONAL IMAGE HELPER
    # ------------------------------------------------------------------
    def get_educational_image(
        self,
        topic: str,
        subject: Optional[str] = None,
    ) -> str:
        topic = (topic or "").strip()
        if subject:
            base = f"{subject} {topic}".strip()
        else:
            base = topic

        enriched = f"{base} educational diagram illustration"
        url = self._search_freepik_for_slide(
            topic=enriched,
            slide=type("DummySlide", (), {"title": base, "image_query": ""})(),
            slide_index=0,
            used_urls=set(),
        )

        if not url:
            url = self._get_placeholder_image(topic or "education")

        return url


# Singleton instance
image_service = ImageService()
