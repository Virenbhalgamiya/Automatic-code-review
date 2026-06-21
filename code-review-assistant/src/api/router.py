from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, status
from fastapi.responses import JSONResponse
from typing import List, Any
from sqlalchemy.sql import text
from src.api.schemas import ScanReport, HealthReport
from src.api.dependencies import get_review_service
from src.services.review_service import ReviewService
from src.database.connection import engine, DatabaseError

router = APIRouter()

@router.post("/analyze", response_model=ScanReport, status_code=status.HTTP_200_OK)
async def analyze_file(
    file: UploadFile = File(...),
    service: ReviewService = Depends(get_review_service)
) -> ScanReport:
    """
    Accepts a Python source file via multipart upload.
    Delegates analysis and database persistence to the service layer.
    """
    if not file.filename.endswith(".py"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Only Python (.py) files are supported."
        )
    
    try:
        content = await file.read()
        file_content = content.decode("utf-8")
    except UnicodeDecodeError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"The uploaded file is not a valid UTF-8 text file: {str(e)}"
        )
    
    try:
        return service.analyze_file(filename=file.filename, file_content=file_content)
    except DatabaseError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database storage failed: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected internal error occurred: {str(e)}"
        )

@router.get("/scans", response_model=List[ScanReport], status_code=status.HTTP_200_OK)
async def get_scans(
    service: ReviewService = Depends(get_review_service)
) -> List[ScanReport]:
    """Retrieves all historical static analysis scan records."""
    try:
        return service.get_all_scans()
    except DatabaseError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database retrieval failed: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected internal error occurred: {str(e)}"
        )

@router.get("/health", response_model=HealthReport, responses={503: {"model": HealthReport}})
async def health_check() -> Any:
    """
    Verifies that the API is running and attempts a real database connection.
    Returns 200 OK if database is reachable, otherwise returns 503 Service Unavailable.
    """
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return HealthReport(status="healthy", database="connected")
    except Exception as e:
        error_msg = f"Database connection check failed: {str(e)}"
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content=HealthReport(
                status="unhealthy",
                database="disconnected",
                error=error_msg
            ).model_dump()
        )
