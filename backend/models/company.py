"""
TenderFit - Company Models
Defines the database schema for Company profiles and uploaded supporting documents.
"""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, Boolean, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from backend.database import Base


def utc_now():
    return datetime.now(timezone.utc)


class Company(Base):
    """
    Represents a registered enterprise profile bidding for government tenders.
    """
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False, index=True)
    business_category = Column(String(100), nullable=False, index=True)
    location = Column(String(150), nullable=False)
    
    # Financial and track record details
    annual_turnover = Column(Float, nullable=False, default=0.0)  # Value in INR
    years_of_experience = Column(Integer, nullable=False, default=0)
    previous_projects_count = Column(Integer, nullable=False, default=0)

    # Statutory Registrations
    gst_registered = Column(Boolean, nullable=False, default=False)
    gst_number = Column(String(30), nullable=True)
    udyam_registered = Column(Boolean, nullable=False, default=False)
    udyam_number = Column(String(50), nullable=True)

    # Specialisations & Capabilities (comma-separated or JSON list)
    specialisations = Column(Text, nullable=True)

    created_at = Column(DateTime, default=utc_now, nullable=False)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)

    # Relationships
    documents = relationship("CompanyDocument", back_populates="company", cascade="all, delete-orphan")
    eligibility_results = relationship("EligibilityResult", back_populates="company", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Company(id={self.id}, name='{self.name}', category='{self.business_category}')>"


class CompanyDocument(Base):
    """
    Represents a supporting document uploaded by a company (GST, PAN, Audited Turnover, etc.).
    """
    __tablename__ = "company_documents"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    
    document_type = Column(String(50), nullable=False)  # GST, PAN, UDYAM, TURNOVER_PROOF, EXPERIENCE_CERT, etc.
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size_bytes = Column(Integer, nullable=False, default=0)
    
    # Optional metadata or extracted details stored as JSON string
    extracted_data_json = Column(Text, nullable=True)
    
    uploaded_at = Column(DateTime, default=utc_now, nullable=False)

    # Relationships
    company = relationship("Company", back_populates="documents")

    def __repr__(self):
        return f"<CompanyDocument(id={self.id}, type='{self.document_type}', file='{self.file_name}')>"

