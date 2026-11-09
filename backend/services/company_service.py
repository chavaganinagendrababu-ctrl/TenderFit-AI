"""
TenderFit - Company Business Logic Service
Handles persistence, retrieval, profile updates, and document attachments.
"""

from pathlib import Path
from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from backend.models.company import Company, CompanyDocument
from backend.schemas.company import CompanyCreate, CompanyUpdate
from config.settings import settings


ALLOWED_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg"}
MAX_FILE_SIZE_BYTES = 15 * 1024 * 1024  # 15 MB limit


class CompanyService:
    @staticmethod
    def get_by_id(db: Session, company_id: int) -> Optional[Company]:
        """Fetch a single company by primary key."""
        return db.query(Company).filter(Company.id == company_id).first()

    @staticmethod
    def get_by_name(db: Session, name: str) -> Optional[Company]:
        """Fetch a company by unique company name."""
        return db.query(Company).filter(Company.name.ilike(name.strip())).first()

    @staticmethod
    def list_companies(db: Session, skip: int = 0, limit: int = 100) -> List[Company]:
        """List all registered companies."""
        return db.query(Company).offset(skip).limit(limit).all()

    @staticmethod
    def create_company(db: Session, data: CompanyCreate) -> Company:
        """Create a new company profile. Rejects duplicates."""
        existing = CompanyService.get_by_name(db, data.name)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Company with name '{data.name}' is already registered."
            )
        
        company = Company(
            name=data.name.strip(),
            business_category=data.business_category.strip(),
            location=data.location.strip(),
            annual_turnover=data.annual_turnover,
            years_of_experience=data.years_of_experience,
            previous_projects_count=data.previous_projects_count,
            gst_registered=data.gst_registered,
            gst_number=data.gst_number.strip() if data.gst_number else None,
            udyam_registered=data.udyam_registered,
            udyam_number=data.udyam_number.strip() if data.udyam_number else None,
            specialisations=data.specialisations.strip() if data.specialisations else None,
        )
        db.add(company)
        db.commit()
        db.refresh(company)
        return company

    @staticmethod
    def update_company(db: Session, company_id: int, data: CompanyUpdate) -> Company:
        """Update fields on an existing company profile."""
        company = CompanyService.get_by_id(db, company_id)
        if not company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Company with ID {company_id} not found."
            )

        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(company, key, value)

        db.commit()
        db.refresh(company)
        return company

    @staticmethod
    def save_company_document(
        db: Session,
        company_id: int,
        document_type: str,
        file_name: str,
        content: bytes,
    ) -> CompanyDocument:
        """Saves an uploaded document safely to disk and creates a database record."""
        company = CompanyService.get_by_id(db, company_id)
        if not company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Company with ID {company_id} not found."
            )

        # 1. File size enforcement
        if len(content) > MAX_FILE_SIZE_BYTES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File exceeds maximum allowed size of 15 MB ({len(content)} bytes)."
            )

        # 2. Path Traversal & Filename sanitization
        base_name = Path(file_name).name
        ext = Path(base_name).suffix.lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File type '{ext}' is not permitted. Allowed: {', '.join(ALLOWED_EXTENSIONS)}."
            )

        import re
        clean_name = re.sub(r'[<>:"/\\|?*]', '_', base_name)
        clean_doc_type = re.sub(r'[<>:"/\\|?*]', '_', document_type.upper().strip())

        # Company-specific folder
        company_folder = settings.COMPANY_DOCS_DIR / f"company_{company_id}"
        company_folder.mkdir(parents=True, exist_ok=True)

        safe_filename = f"{clean_doc_type}_{clean_name}"
        dest_path = company_folder / safe_filename
        with open(dest_path, "wb") as f:
            f.write(content)

        doc = CompanyDocument(
            company_id=company_id,
            document_type=clean_doc_type,
            file_name=clean_name,
            file_path=str(dest_path),
            file_size_bytes=len(content),
        )
        db.add(doc)
        db.commit()
        db.refresh(doc)
        return doc

