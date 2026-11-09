"""
TenderFit - Pydantic Schemas for Company Registration and Management
Provides strict input validation and serialized API response models.
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator, ConfigDict


class CompanyBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=255, description="Full registered legal company name")
    business_category: str = Field(..., min_length=2, max_length=100, description="Primary business sector (e.g. Civil Construction)")
    location: str = Field(..., min_length=2, max_length=150, description="Headquarters city, state")
    annual_turnover: float = Field(..., ge=0, description="Annual turnover in Indian Rupees (INR)")
    years_of_experience: int = Field(..., ge=0, description="Years in operational business")
    previous_projects_count: int = Field(..., ge=0, description="Total successfully completed projects")
    gst_registered: bool = Field(default=False, description="Whether company possesses active GSTIN")
    gst_number: Optional[str] = Field(None, max_length=30, description="15-character GSTIN if registered")
    udyam_registered: bool = Field(default=False, description="Whether MSME / Udyam registered")
    udyam_number: Optional[str] = Field(None, max_length=50, description="Udyam Registration Number if registered")
    specialisations: Optional[str] = Field(None, description="Comma-separated or textual summary of core competencies")

    @field_validator("gst_number")
    @classmethod
    def validate_gst(cls, v, values):
        if v and len(v.strip()) > 0:
            v = v.strip().upper()
        return v

    @field_validator("name")
    @classmethod
    def clean_name(cls, v):
        return v.strip()


class CompanyCreate(CompanyBase):
    pass


class CompanyUpdate(BaseModel):
    name: Optional[str] = None
    business_category: Optional[str] = None
    location: Optional[str] = None
    annual_turnover: Optional[float] = Field(None, ge=0)
    years_of_experience: Optional[int] = Field(None, ge=0)
    previous_projects_count: Optional[int] = Field(None, ge=0)
    gst_registered: Optional[bool] = None
    gst_number: Optional[str] = None
    udyam_registered: Optional[bool] = None
    udyam_number: Optional[str] = None
    specialisations: Optional[str] = None


class CompanyDocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    company_id: int
    document_type: str
    file_name: str
    file_path: str
    file_size_bytes: int
    uploaded_at: datetime


class CompanyResponse(CompanyBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
    documents: List[CompanyDocumentResponse] = []

