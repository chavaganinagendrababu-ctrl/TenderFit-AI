"""
TenderFit - API & Service Client for Streamlit
Connects the frontend to FastAPI backend endpoints with graceful fallback to DB services.
"""

import sys
from pathlib import Path

# Ensure project root is always on sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import requests
import logging
from typing import Dict, Any, List, Optional
from config.settings import settings
from backend.database import SessionLocal
from backend.services.company_service import CompanyService
from backend.services.tender_service import TenderService
from backend.schemas.company import CompanyCreate, CompanyUpdate

logger = logging.getLogger("tenderfit.frontend.client")


class TenderFitClient:
    """Unified client for Streamlit frontend."""

    def __init__(self, base_url: Optional[str] = None):
        self.base_url = (base_url or settings.API_BASE_URL).rstrip("/")

    def is_backend_online(self) -> bool:
        """Checks if FastAPI backend server is actively responding."""
        try:
            resp = requests.get(f"{self.base_url}/api/health", timeout=1.5)
            return resp.status_code == 200
        except Exception:
            return False

    def list_companies(self) -> List[Dict[str, Any]]:
        """Retrieves list of companies."""
        if self.is_backend_online():
            try:
                resp = requests.get(f"{self.base_url}/api/companies/", timeout=3.0)
                if resp.status_code == 200:
                    return resp.json()
            except Exception as e:
                logger.warning(f"FastAPI request failed: {e}. Falling back to DB service.")

        # Fallback to direct DB session
        db = SessionLocal()
        try:
            companies = CompanyService.list_companies(db)
            return [
                {
                    "id": c.id,
                    "name": c.name,
                    "business_category": c.business_category,
                    "location": c.location,
                    "annual_turnover": c.annual_turnover,
                    "years_of_experience": c.years_of_experience,
                    "previous_projects_count": c.previous_projects_count,
                    "gst_registered": c.gst_registered,
                    "gst_number": c.gst_number,
                    "udyam_registered": c.udyam_registered,
                    "udyam_number": c.udyam_number,
                    "specialisations": c.specialisations,
                    "documents": [
                        {
                            "id": d.id,
                            "document_type": d.document_type,
                            "file_name": d.file_name,
                            "file_size_bytes": d.file_size_bytes,
                            "uploaded_at": str(d.uploaded_at),
                        }
                        for d in c.documents
                    ],
                }
                for c in companies
            ]
        finally:
            db.close()

    def get_company(self, company_id: int) -> Optional[Dict[str, Any]]:
        """Fetch single company details."""
        if self.is_backend_online():
            try:
                resp = requests.get(f"{self.base_url}/api/companies/{company_id}", timeout=3.0)
                if resp.status_code == 200:
                    return resp.json()
            except Exception:
                pass

        db = SessionLocal()
        try:
            c = CompanyService.get_by_id(db, company_id)
            if not c:
                return None
            return {
                "id": c.id,
                "name": c.name,
                "business_category": c.business_category,
                "location": c.location,
                "annual_turnover": c.annual_turnover,
                "years_of_experience": c.years_of_experience,
                "previous_projects_count": c.previous_projects_count,
                "gst_registered": c.gst_registered,
                "gst_number": c.gst_number,
                "udyam_registered": c.udyam_registered,
                "udyam_number": c.udyam_number,
                "specialisations": c.specialisations,
                "documents": [
                    {
                        "id": d.id,
                        "document_type": d.document_type,
                        "file_name": d.file_name,
                        "file_size_bytes": d.file_size_bytes,
                        "uploaded_at": str(d.uploaded_at),
                    }
                    for d in c.documents
                ],
            }
        finally:
            db.close()

    def register_company(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Registers a new company."""
        if self.is_backend_online():
            resp = requests.post(f"{self.base_url}/api/companies/", json=payload, timeout=5.0)
            if resp.status_code == 201:
                return resp.json()
            else:
                detail = resp.json().get("detail", "Failed to register company via API.")
                raise Exception(detail)

        # Fallback to direct DB service
        db = SessionLocal()
        try:
            dto = CompanyCreate(**payload)
            c = CompanyService.create_company(db, dto)
            return {"id": c.id, "name": c.name, "business_category": c.business_category}
        finally:
            db.close()

    def upload_document(self, company_id: int, document_type: str, file_name: str, file_bytes: bytes) -> Dict[str, Any]:
        """Uploads a supporting document."""
        if self.is_backend_online():
            files = {"file": (file_name, file_bytes)}
            data = {"document_type": document_type}
            resp = requests.post(f"{self.base_url}/api/companies/{company_id}/documents", data=data, files=files, timeout=10.0)
            if resp.status_code == 201:
                return resp.json()
            else:
                raise Exception(resp.text)

        # Fallback to direct DB service
        db = SessionLocal()
        try:
            doc = CompanyService.save_company_document(
                db=db,
                company_id=company_id,
                document_type=document_type,
                file_name=file_name,
                content=file_bytes,
            )
            return {"id": doc.id, "file_name": doc.file_name, "document_type": doc.document_type}
        finally:
            db.close()

    def list_tenders(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """List tenders."""
        if self.is_backend_online():
            try:
                params = {"category": category} if category else {}
                resp = requests.get(f"{self.base_url}/api/tenders/", params=params, timeout=3.0)
                if resp.status_code == 200:
                    return resp.json()
            except Exception:
                pass

        db = SessionLocal()
        try:
            tenders = TenderService.list_tenders(db, category=category)
            return [
                {
                    "id": t.id,
                    "tender_id": t.tender_id,
                    "title": t.title,
                    "department": t.department,
                    "location": t.location,
                    "estimated_value": t.estimated_value,
                    "closing_date": str(t.closing_date) if t.closing_date else "Open",
                    "tender_url": t.tender_url,
                    "pdf_path": t.pdf_path,
                    "portal_name": t.portal_name,
                    "category": t.category,
                }
                for t in tenders
            ]
        finally:
            db.close()


client = TenderFitClient()

