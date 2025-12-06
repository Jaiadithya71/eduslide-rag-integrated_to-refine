from fastapi import APIRouter, HTTPException, status
from fastapi.responses import FileResponse
import os

from backend.app.models.schemas import (
    PresentationRequest,
    PresentationResponse,
    HealthResponse,
    ErrorResponse
)
from backend.app.services.presentation_service import presentation_service
from backend.app.core.config import settings


# Create API router
router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        version=settings.PROJECT_VERSION,
        environment=settings.ENVIRONMENT,
        services={
            "groq": "configured" if settings.GROQ_API_KEY else "not configured",
            "freepik": "configured" if settings.FREEPIK_API_KEY else "not configured",
            "qdrant": "pending"
        }
    )


@router.post(
    "/generate",
    response_model=PresentationResponse,
    status_code=status.HTTP_201_CREATED
)
async def generate_presentation(request: PresentationRequest):
    """
    Generate a new presentation.

    This endpoint:
    1. Validates the request
    2. Generates slide content using Groq AI (FREE Llama 3.1)
    3. Fetches relevant images from Pexels (FREE)
    4. Builds and saves a PPTX file on disk
    5. Returns structured slide data + metadata (client handles download)
    """
    try:
        # Validate request
        is_valid, error_message = presentation_service.validate_request(request)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_message
            )

        # Generate presentation (slides + PPTX)
        presentation = await presentation_service.generate_presentation(request)
        return presentation

    except HTTPException:
        # Re-raise HTTP exceptions directly
        raise
    except Exception as e:
        print(f"Error in generate_presentation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate presentation: {str(e)}"
        )


@router.get("/download/{presentation_id}")
async def download_presentation(presentation_id: str):
    """
    Download a generated PowerPoint (.pptx) file by presentation ID.
    The file is created by PresentationService and stored in 'generated_presentations/'.
    """
    # Compute path to generated_presentations folder (backend root)
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    presentations_dir = os.path.join(base_dir, "generated_presentations")
    filename = f"eduslide_ai_{presentation_id}.pptx"
    file_path = os.path.join(presentations_dir, filename)

    if not os.path.exists(file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Presentation file not found"
        )

    return FileResponse(
        file_path,
        media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
        filename=filename
    )


@router.get("/presentation/{presentation_id}")
async def get_presentation(presentation_id: str):
    """
    Retrieve a generated presentation by ID.

    NOTE:
    - Full persistence (database/Qdrant) is not implemented yet.
    - For now, this endpoint simply reports that storage is not implemented.
    - The frontend uses /download/{presentation_id} for actual file download.
    """
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Presentation storage will be implemented in Phase 2 with Qdrant"
    )


@router.get("/presentations")
async def list_presentations(skip: int = 0, limit: int = 10):
    """
    List all generated presentations.

    Note: This is a placeholder for Phase 2 when we add database storage.
    """
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Presentation listing will be implemented in Phase 2 with Qdrant"
    )
