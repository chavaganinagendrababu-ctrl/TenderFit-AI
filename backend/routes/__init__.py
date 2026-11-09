"""Routes package for TenderFit."""
from backend.routes.companies import router as companies_router
from backend.routes.tenders import router as tenders_router
from backend.routes.logs import router as logs_router

__all__ = ["companies_router", "tenders_router", "logs_router"]

