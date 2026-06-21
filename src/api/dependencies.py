from src.services.review_service import ReviewService

def get_review_service() -> ReviewService:
    """Dependency provider for ReviewService."""
    return ReviewService()
