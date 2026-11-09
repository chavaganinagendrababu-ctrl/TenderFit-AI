"""
Integration Tests for FastAPI Route Handlers
Tests company registration, retrieval, listing, and validation endpoints.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi import HTTPException

from backend.database import Base
from backend.schemas.company import CompanyCreate, CompanyUpdate
from backend.routes.companies import register_company, get_company, list_companies
from backend.main import root, health_check


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSession()
    try:
        yield session
    finally:
        session.close()


def test_health_endpoints():
    r = root()
    assert r["app"] == "TenderFit"
    h = health_check()
    assert h["status"] == "healthy"


def test_company_api_flow(db_session):
    payload = CompanyCreate(
        name="FastAPI Tenders Pvt. Ltd.",
        business_category="Road Infrastructure & Civil Construction",
        location="Hyderabad, Telangana",
        annual_turnover=60000000.0,
        years_of_experience=6,
        previous_projects_count=12,
        gst_registered=True,
        gst_number="36ABCDE1234F1Z5",
        udyam_registered=True,
        udyam_number="UDYAM-TS-01-0012345",
        specialisations="Highway expansion, toll plaza construction",
    )
    # 1. Register
    created = register_company(company_in=payload, db=db_session)
    assert created.id is not None
    assert created.name == "FastAPI Tenders Pvt. Ltd."

    # 2. Get by ID
    fetched = get_company(company_id=created.id, db=db_session)
    assert fetched.id == created.id
    assert fetched.annual_turnover == 60000000.0

    # 3. List
    all_comps = list_companies(db=db_session)
    assert len(all_comps) == 1


def test_duplicate_company_api_rejected(db_session):
    payload = CompanyCreate(
        name="Duplicate Test Corp",
        business_category="IT",
        location="Chennai",
        annual_turnover=1000000.0,
        years_of_experience=1,
        previous_projects_count=1,
        gst_registered=False,
    )
    register_company(company_in=payload, db=db_session)

    # Duplicate should raise HTTPException 400
    with pytest.raises(HTTPException) as exc_info:
        register_company(company_in=payload, db=db_session)
    assert exc_info.value.status_code == 400
