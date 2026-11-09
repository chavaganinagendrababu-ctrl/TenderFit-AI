"""
Unit Tests for Company Pydantic Schemas and Validation Logic
"""

import pytest
from pydantic import ValidationError
from backend.schemas.company import CompanyCreate, CompanyUpdate


def test_valid_company_creation():
    data = {
        "name": "Apex Infra Projects Pvt. Ltd.",
        "business_category": "Road Infrastructure & Civil Construction",
        "location": "Mumbai, Maharashtra",
        "annual_turnover": 50000000.0,
        "years_of_experience": 5,
        "previous_projects_count": 8,
        "gst_registered": True,
        "gst_number": "27aaaaa0000a1z5",
        "udyam_registered": True,
        "udyam_number": "UDYAM-MH-01-0012345",
        "specialisations": "Highway construction, asphalt paving",
    }
    company = CompanyCreate(**data)
    assert company.name == "Apex Infra Projects Pvt. Ltd."
    # GST should be automatically normalized to uppercase
    assert company.gst_number == "27AAAAA0000A1Z5"
    assert company.annual_turnover == 50000000.0


def test_negative_turnover_rejected():
    with pytest.raises(ValidationError):
        CompanyCreate(
            name="Invalid Co",
            business_category="Construction",
            location="Delhi",
            annual_turnover=-500.0,  # Invalid negative
            years_of_experience=2,
            previous_projects_count=1,
            gst_registered=False,
        )


def test_negative_experience_rejected():
    with pytest.raises(ValidationError):
        CompanyCreate(
            name="Invalid Co",
            business_category="Construction",
            location="Delhi",
            annual_turnover=100000.0,
            years_of_experience=-1,  # Invalid negative
            previous_projects_count=1,
            gst_registered=False,
        )

