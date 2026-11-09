"""
TenderFit - Company API Routes
Endpoints for registering, viewing, updating companies and uploading documents.
"""

from typing import List
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.schemas.company import (
    CompanyCreate,
    CompanyUpdate,
    CompanyResponse,
    CompanyDocumentResponse,
)
from backend.services.company_service import CompanyService

router = APIRouter(prefix="/api/companies", tags=["Companies"])


@router.post("/", response_model=CompanyResponse, status_code=status.HTTP_201_CREATED)
def register_company(company_in: CompanyCreate, db: Session = Depends(get_db)):
    """
    Registers a new enterprise profile in TenderFit.
    Validates company turnover, experience, and registration criteria.
    """
    return CompanyService.create_company(db, company_in)


@router.get("/", response_model=List[CompanyResponse])
def list_companies(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """List all registered company profiles."""
    return CompanyService.list_companies(db, skip=skip, limit=limit)


@router.get("/{company_id}", response_model=CompanyResponse)
def get_company(company_id: int, db: Session = Depends(get_db)):
    """Retrieve details for a specific registered company."""
    company = CompanyService.get_by_id(db, company_id)
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Company with ID {company_id} not found."
        )
    return company


@router.put("/{company_id}", response_model=CompanyResponse)
def update_company(company_id: int, company_in: CompanyUpdate, db: Session = Depends(get_db)):
    """Update profile attributes of a registered company."""
    return CompanyService.update_company(db, company_id, company_in)


@router.post("/{company_id}/documents", response_model=CompanyDocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_company_document(
    company_id: int,
    document_type: str = Form(..., description="Document type: GST, PAN, UDYAM, TURNOVER_PROOF, EXPERIENCE_CERT, etc."),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """
    Upload and attach a supporting document (PDF, image, or doc) to the company profile.
    Saves document to disk and creates a secure database reference.
    """
    content = await file.read()
    if not content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The uploaded file is empty."
        )

    doc = CompanyService.save_company_document(
        db=db,
        company_id=company_id,
        document_type=document_type,
        file_name=file.filename or "uploaded_doc.pdf",
        content=content,
    )
    return doc

