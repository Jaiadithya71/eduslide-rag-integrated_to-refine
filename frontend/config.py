"""
Frontend configuration for EduSlide AI (Streamlit app).

This file defines:
- App branding
- Backend URL
- The options shown in dropdowns (audience, style, language, complexity)
"""

from dataclasses import dataclass


@dataclass
class Config:
    # Basic app info
    APP_TITLE: str = "EduSlide AI – Smart Slide Generator"
    APP_VERSION: str = "1.0.0"
    PAGE_ICON: str = "🎓"

    # Backend API base URL
    # Dynamically read from file if available (set by start.ps1)
    def _get_backend_url():
        import os
        from pathlib import Path
        try:
            # Current file is in frontend/, so project root is one level up
            root_dir = Path(__file__).parent.parent
            port_file = root_dir / ".backend_port"
            if port_file.exists():
                port = port_file.read_text().strip()
                if port.isdigit():
                    return f"http://localhost:{port}"
        except Exception:
            pass
        return "http://localhost:8000"

    BACKEND_URL: str = _get_backend_url()

    # Audience options (what user sees in dropdown)
    AUDIENCE_TYPES = [
        "School students (6–10)",
        "High school students (11–12)",
        "College / University",
        "Professional training",
        "Technical briefing",
        "Business presentation",
    ]

    # Presentation style options (what user sees)
    PRESENTATION_STYLES = [
        "Academic",
        "Storytelling",
        "Business pitch",
        "Technical deep-dive",
        "Workshop / interactive",
        "Minimalist",
    ]

    # Supported languages (frontend labels)
    LANGUAGES = [
        "English",
        "Hindi",
        "Bilingual (English + Hindi)",
    ]

    # Content depth / complexity
    COMPLEXITY_LEVELS = [
        "Beginner",
        "Intermediate",
        "Advanced",
        "Expert",
    ]

    # Slide count defaults
    MIN_SLIDES: int = 5
    MAX_SLIDES: int = 15
    DEFAULT_SLIDES: int = 10
