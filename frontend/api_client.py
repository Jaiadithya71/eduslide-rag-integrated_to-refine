"""
API client for talking to the FastAPI backend from Streamlit.

- Handles health check
- Sends normalized, backend-safe payloads
- Maps rich UI options (Gamma-style) into:
  * backend enums
  * extra context in the topic for the LLM
- Fetches PPTX bytes for download
"""

import requests
from typing import Any, Dict, Optional

from config import Config


class APIClient:
    def __init__(self) -> None:
        self.base_url = Config.BACKEND_URL.rstrip("/")

    # --------------------------------------------------
    # HEALTH CHECK
    # --------------------------------------------------
    def check_health(self) -> Dict[str, Any]:
        try:
            resp = requests.get(f"{self.base_url}/health", timeout=5)
            resp.raise_for_status()
            data = resp.json()
            # Ensure a consistent shape for the Streamlit sidebar
            return {
                "status": data.get("status", "unknown"),
                "version": data.get("version", Config.APP_VERSION),
            }
        except Exception as e:
            print("[APIClient] Health check error:", e)
            return {"status": "offline", "version": None}

    # --------------------------------------------------
    # PUBLIC: Generate presentation
    # --------------------------------------------------
    def generate_presentation(
        self,
        topic: str,
        audience_type: str,
        num_slides: int,
        style: str,
        language: str,
        complexity: str,
        include_images: bool,
        include_notes: bool,
    ) -> Dict[str, Any]:
        """
        Call backend /generate with:
        - normalized enums the backend expects
        - rich topic containing all user options (Gamma-like control)
        """

        # 1. Normalize options to backend-safe enums
        backend_audience = self._normalize_audience(audience_type)
        backend_style = self._normalize_style(style)
        backend_language = self._normalize_language(language)
        backend_complexity = self._normalize_complexity(complexity)

        # 2. Build a "rich topic" that encodes all options for the LLM
        rich_topic = self._build_rich_topic(
            topic=topic,
            audience_label=audience_type,
            style_label=style,
            language_label=language,
            complexity_label=complexity,
        )

        payload = {
            "topic": rich_topic,
            "audience_type": backend_audience,
            "num_slides": num_slides,
            "presentation_style": backend_style,
            "language": backend_language,
            "complexity": backend_complexity,
            "include_images": include_images,
            "include_quiz": False,        # you can later toggle this via UI
            "speaker_notes": include_notes,
        }

        try:
            resp = requests.post(
                f"{self.base_url}/generate",
                json=payload,
                timeout=300,  # 5 minutes for Gemini-powered generation
            )
            if resp.status_code != 201:
                # backend returned an error (422, 500, etc.)
                try:
                    err_json = resp.json()
                except Exception:
                    err_json = {"detail": resp.text}
                print("[APIClient] Generate error:", resp.status_code, err_json)
                return {
                    "status": "error",
                    "message": f"HTTP {resp.status_code}: {err_json}",
                }

            data = resp.json()

            # Extract key info from backend response
            presentation_id = data.get("presentation_id")
            slides = data.get("slides", [])
            total_slides = data.get("total_slides", len(slides))
            generation_time = data.get("generation_time", 0.0)

            # Try downloading PPTX bytes (optional but nice)
            file_bytes: Optional[bytes] = None
            filename: str = f"eduslide_ai_{presentation_id}.pptx"
            download_url = f"{self.base_url}/download/{presentation_id}"

            if presentation_id:
                try:
                    file_resp = requests.get(download_url, timeout=60)
                    if file_resp.status_code == 200:
                        file_bytes = file_resp.content
                    else:
                        print(
                            "[APIClient] PPTX download error:",
                            file_resp.status_code,
                            file_resp.text,
                        )
                except Exception as e:
                    print("[APIClient] PPTX download exception:", e)

            # Count how many slides actually got images
            images_added = sum(
                1 for s in slides if s.get("image_url") not in (None, "")
            )

            # Build unified response for Streamlit
            return {
                "status": "success",
                "message": None,
                "presentation_id": presentation_id,
                "slides": slides,
                "total_slides": total_slides,
                "generation_time": generation_time,
                "has_notes": bool(include_notes),
                "download_url": download_url,
                "file_data": file_bytes,
                "filename": filename,
                "images_added": images_added,
            }

        except Exception as e:
            print("[APIClient] Exception in generate_presentation:", e)
            return {
                "status": "error",
                "message": f"Exception while calling backend: {e}",
            }

    # --------------------------------------------------
    # NORMALIZATION HELPERS
    # Map rich UI labels to backend-safe enums
    # --------------------------------------------------
    def _normalize_audience(self, audience_label: str) -> str:
        """
        Backend expects one of:
        - 'elementary', 'middle', 'high', 'college', 'professional'

        We map your UI options to these buckets.
        """
        text = (audience_label or "").lower()

        if "6" in text or "school students" in text:
            return "elementary"
        if "11-12" in text or "high school" in text:
            return "high"
        if "college" in text or "university" in text:
            return "college"
        if "technical briefing" in text:
            return "professional"
        if "business presentation" in text:
            return "professional"
        if "professional training" in text:
            return "professional"

        # Safe default
        return "college"

    def _normalize_style(self, style_label: str) -> str:
        """
        Backend expects:
        - 'academic', 'storytelling', 'interactive', 'technical', 'visual'
        """
        text = (style_label or "").lower()

        if "academic" in text:
            return "academic"
        if "story" in text:
            return "storytelling"
        if "business" in text or "pitch" in text:
            # Business pitch is usually visual + persuasive
            return "visual"
        if "deep" in text or "technical" in text:
            return "technical"
        if "workshop" in text or "interactive" in text:
            return "interactive"
        if "minimalist" in text:
            return "visual"

        # Fallback
        return "academic"

    def _normalize_language(self, lang_label: str) -> str:
        """
        Map frontend labels to backend Language enum values.
        Assuming backend Language enum accepts:
        - 'english', 'hindi', 'bilingual'
        """
        text = (lang_label or "").lower()
        if "bilingual" in text:
            return "bilingual"
        if "hindi" in text:
            return "hindi"
        return "english"

    def _normalize_complexity(self, complexity_label: str) -> str:
        """
        Forward the complexity as a simple lowercase string.

        If backend uses an enum, it likely expects:
        - 'beginner', 'intermediate', 'advanced', 'expert'
        """
        text = (complexity_label or "intermediate").strip().lower()
        valid = {"beginner", "intermediate", "advanced", "expert"}
        return text if text in valid else "intermediate"

    # --------------------------------------------------
    # RICH TOPIC FOR LLM
    # --------------------------------------------------
    def _build_rich_topic(
        self,
        topic: str,
        audience_label: str,
        style_label: str,
        language_label: str,
        complexity_label: str,
    ) -> str:
        """
        Gamma-like: we pass all user choices into the topic description
        so the LLM can adapt tone, depth, and format.

        Example:
        "Understanding AI for Beginners
         [Audience: College / University | Style: Technical deep-dive |
          Language: English | Complexity: Intermediate]"
        """
        base = (topic or "").strip()

        meta = (
            f"Audience: {audience_label}; "
            f"Style: {style_label}; "
            f"Language: {language_label}; "
            f"Complexity: {complexity_label}"
        )

        return f"{base}  [{meta}]"
