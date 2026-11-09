"""
Integration Tests for Database Operations and Company Service
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.database import Base
from backend.models.company import Company, CompanyDocument
from backend.schemas.company import CompanyCreate, CompanyUpdate
from backend.services.company_service import CompanyService


@pytest.fixture
def test_db():
    """In-memory SQLite session for isolated database testing."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


def test_create_and_retrieve_company(test_db):
    dto = CompanyCreate(
        name="BuildTech Highway Solutions",
        business_category="Road Infrastructure & Civil Construction",
        location="Pune, Maharashtra",
        annual_turnover=35000000.0,
        years_of_experience=4,
        previous_projects_count=6,
        gst_registered=True,
        gst_number="27ABCDE1234F1Z5",
        udyam_registered=True,
        udyam_number="UDYAM-MH-02-9876543",
        specialisations="Bitumen laying, concrete paving",
    )
    created = CompanyService.create_company(test_db, dto)
    assert created.id is not None
    assert created.name == "BuildTech Highway Solutions"

    # Query back
    retrieved = CompanyService.get_by_id(test_db, created.id)
    assert retrieved is not None
    assert retrieved.annual_turnover == 35000000.0
    assert retrieved.years_of_experience == 4


def test_duplicate_company_rejected(test_db):
    dto = CompanyCreate(
        name="Unique Infra Corp",
        business_category="Construction",
        location="Delhi",
        annual_turnover=10000000.0,
        years_of_experience=2,
        previous_projects_count=3,
        gst_registered=False,
    )
    CompanyService.create_company(test_db, dto)

    # Attempt duplicate name registration
    with pytest.raises(Exception):
        CompanyService.create_company(test_db, dto)


def test_update_company_profile(test_db):
    dto = CompanyCreate(
        name="Prime Electrics",
        business_category="Electrical Works",
        location="Bengaluru, Karnataka",
        annual_turnover=20000000.0,
        years_of_experience=3,
        previous_projects_count=5,
        gst_registered=True,
    )
    comp = CompanyService.create_company(test_db, dto)

    # Update turnover and experience
    update_dto = CompanyUpdate(annual_turnover=45000000.0, years_of_experience=5)
    updated = CompanyService.update_company(test_db, comp.id, update_dto)
    assert updated.annual_turnover == 45000000.0
    assert updated.years_of_experience == 5

