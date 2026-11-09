"""
TenderFit - Tender and Eligibility Models
Defines schemas for discovered tenders, extracted requirements, and match assessments.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from backend.database import Base


class Tender(Base):
    """
    Represents a public government tender discovered via browser automation or ingestion.
    """
    __tablename__ = "tenders"

    id = Column(Integer, primary_key=True, index=True)
    tender_id = Column(String(100), unique=True, nullable=False, index=True)
    title = Column(String(500), nullable=False)
    department = Column(String(255), nullable=False, index=True)
    location = Column(String(150), nullable=False)
    
    estimated_value = Column(Float, nullable=True)  # In INR
    closing_date = Column(DateTime, nullable=True)
    
    tender_url = Column(String(1000), nullable=False)
    pdf_path = Column(String(500), nullable=True)
    portal_name = Column(String(100), nullable=False, default="Public Tender Portal")
    category = Column(String(100), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    requirements = relationship("TenderRequirement", back_populates="tender", uselist=False, cascade="all, delete-orphan")
    eligibility_results = relationship("EligibilityResult", back_populates="tender", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Tender(id={self.id}, tender_id='{self.tender_id}', title='{self.title[:30]}...')>"


class TenderRequirement(Base):
    """
    Structured requirements extracted from tender document text or AI analysis.
    """
    __tablename__ = "tender_requirements"

    id = Column(Integer, primary_key=True, index=True)
    tender_id = Column(Integer, ForeignKey("tenders.id", ondelete="CASCADE"), unique=True, nullable=False)

    # Core quantifiable criteria
    minimum_turnover = Column(Float, nullable=True)          # In INR
    minimum_experience_years = Column(Integer, nullable=True)
    minimum_similar_projects = Column(Integer, nullable=True)
    gst_required = Column(Boolean, nullable=False, default=True)
    emd_amount = Column(Float, nullable=True)                 # Earnest Money Deposit in INR

    # Textual criteria & certifications
    required_certificates = Column(Text, nullable=True)       # e.g. ISO 9001, Class A Contractor
    technical_qualifications = Column(Text, nullable=True)

    # Raw extracted JSON for traceability
    raw_conditions_json = Column(Text, nullable=True)
    evidence_clauses_json = Column(Text, nullable=True)       # Exact clauses extracted from PDF for auditability

    extracted_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    tender = relationship("Tender", back_populates="requirements")


class EligibilityResult(Base):
    """
    Computed eligibility outcome comparing a company against a specific tender's requirements.
    """
    __tablename__ = "eligibility_results"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    tender_id = Column(Integer, ForeignKey("tenders.id", ondelete="CASCADE"), nullable=False, index=True)

    # Overall outcome: MET, MISSING, NEEDS VERIFICATION, NOT APPLICABLE
    overall_status = Column(String(50), nullable=False)
    match_score = Column(Float, nullable=False, default=0.0)  # Indicative percentage 0.0 - 100.0

    # Structured details
    details_json = Column(Text, nullable=True)               # Criterion-by-criterion evaluation breakdown
    missing_documents_json = Column(Text, nullable=True)     # Missing certificates or proofs list
    verification_warnings_json = Column(Text, nullable=True) # Items requiring manual clarification

    evaluated_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    company = relationship("Company", back_populates="eligibility_results")
    tender = relationship("Tender", back_populates="eligibility_results")

    def __repr__(self):
        return f"<EligibilityResult(company_id={self.company_id}, tender_id={self.tender_id}, status='{self.overall_status}')>"

