"""
TenderFit - Pydantic Schemas for Tenders, Requirements, and Matching
"""

from datetime import datetime
from typing import Optional, List, Any
from pydantic import BaseModel, Field, ConfigDict


class TenderBase(BaseModel):
    tender_id: str = Field(..., max_length=100)
    title: str = Field(..., max_length=500)
    department: str = Field(..., max_length=255)
    location: str = Field(..., max_length=150)
    estimated_value: Optional[float] = Field(None, ge=0)
    closing_date: Optional[datetime] = None
    tender_url: str = Field(..., max_length=1000)
    pdf_path: Optional[str] = None
    portal_name: str = "Public Tender Portal"
    category: Optional[str] = None


class TenderCreate(TenderBase):
    pass


class TenderRequirementResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    tender_id: int
    minimum_turnover: Optional[float] = None
    minimum_experience_years: Optional[int] = None
    minimum_similar_projects: Optional[int] = None
    gst_required: bool = True
    emd_amount: Optional[float] = None
    required_certificates: Optional[str] = None
    technical_qualifications: Optional[str] = None
    extracted_at: datetime


class EligibilityResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    company_id: int
    tender_id: int
    overall_status: str
    match_score: float
    details_json: Optional[str] = None
    missing_documents_json: Optional[str] = None
    verification_warnings_json: Optional[str] = None
    evaluated_at: datetime


class TenderResponse(TenderBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
    requirements: Optional[TenderRequirementResponse] = None

