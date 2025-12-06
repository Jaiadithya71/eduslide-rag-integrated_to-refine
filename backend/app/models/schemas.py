from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum

class AudienceLevel(str, Enum):
    """Audience level for presentation."""
    ELEMENTARY = "elementary"
    MIDDLE = "middle"
    HIGH = "high"
    COLLEGE = "college"
    PROFESSIONAL = "professional"
class PresentationStyle(str, Enum):
    """Presentation style options."""
    ACADEMIC = "academic"
    STORYTELLING = "storytelling"
    INTERACTIVE = "interactive"
    TECHNICAL = "technical"
    VISUAL = "visual"
class Language(str, Enum):
    """Language options."""
    ENGLISH = "english"
    HINDI = "hindi"
    BILINGUAL = "bilingual"
class ColorTheme(str, Enum):
    """Color theme options."""
    BLUE = "blue"
    PURPLE = "purple"
    GREEN = "green"
    ORANGE = "orange"
class SlideType(str, Enum):
    """Types of slides."""
    TITLE = "title"
    CONTENT = "content"
    QUIZ = "quiz"
    SUMMARY = "summary"
    IMAGE_HEAVY = "image_heavy"
class PresentationRequest(BaseModel):
    """Request model for presentation generation."""
    topic: str = Field(..., description="Topic or lesson outline", min_length=5)
    audience_type: AudienceLevel = Field(default=AudienceLevel.MIDDLE, alias="audience_level")
    num_slides: int = Field(default=6, ge=3, le=15)
    presentation_style: PresentationStyle = Field(default=PresentationStyle.ACADEMIC)
    language: Language = Field(default=Language.ENGLISH)
    include_images: bool = Field(default=True)
    include_quiz: bool = Field(default=False)
    speaker_notes: bool = Field(default=False)
    color_theme: ColorTheme = Field(default=ColorTheme.PURPLE)
    
    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "topic": "Photosynthesis for Class 10 students",
                "audience_level": "middle",
                "num_slides": 6,
                "presentation_style": "academic",
                "language": "english",
                "include_quiz": True,
                "speaker_notes": True,
                "color_theme": "blue"
            }
        }
class SlideContent(BaseModel):
    """Individual slide content."""
    type: SlideType
    title: str
    subtitle: Optional[str] = None
    content: List[str] | str = []
    image_url: Optional[str] = None
    image_query: Optional[str] = None
    speaker_notes: Optional[str] = None
    layout: Optional[str] = "default"
class PresentationResponse(BaseModel):
    """Response model for generated presentation."""
    presentation_id: str
    metadata: PresentationRequest
    slides: List[SlideContent]
    total_slides: int
    created_at: str
    generation_time: float
    
    class Config:
        json_schema_extra = {
            "example": {
                "presentation_id": "pres_123456",
                "metadata": {
                    "topic": "Photosynthesis",
                    "audience_level": "middle",
                    "num_slides": 6
                },
                "slides": [],
                "total_slides": 6,
                "created_at": "2024-11-20T10:30:00",
                "generation_time": 12.5
            }
        }
class ErrorResponse(BaseModel):
    """Error response model."""
    error: str
    detail: Optional[str] = None
    status_code: int
class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    version: str
    environment: str
    services: Dict[str, str]