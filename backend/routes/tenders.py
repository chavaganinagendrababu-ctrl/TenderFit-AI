"""
TenderFit - Tender API Routes
Endpoints to query discovered tenders, view tender details, and register newly scraped tenders.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.schemas.tender import TenderCreate, TenderResponse
from backend.services.tender_service import TenderService

router = APIRouter(prefix="/api/tenders", tags=["Tenders"])


@router.get("/", response_model=List[TenderResponse])
def list_tenders(
    category: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """Retrieve all available tenders with optional business category filter."""
    return TenderService.list_tenders(db, category=category, skip=skip, limit=limit)


@router.get("/{tender_id}", response_model=TenderResponse)
def get_tender(tender_id: str, db: Session = Depends(get_db)):
    """Fetch tender details by unique tender ID."""
    tender = TenderService.get_by_tender_id(db, tender_id)
    if not tender:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tender '{tender_id}' not found."
        )
    return tender


@router.post("/", response_model=TenderResponse, status_code=status.HTTP_201_CREATED)
def create_tender(tender_in: TenderCreate, db: Session = Depends(get_db)):
    """Add or update a tender discovered through the automation engine."""
    return TenderService.create_or_update_tender(db, tender_in)

