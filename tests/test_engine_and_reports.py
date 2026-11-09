"""
Unit Tests for Eligibility Matching Engine, Heuristic Requirements Extraction, and Report Generation
"""

import pytest
from ai.gemini_service import GeminiRequirementExtractor
from eligibility.matching_engine import EligibilityMatchingEngine
from reports.report_generator import ReportGenerator


def test_heuristic_requirement_extractor():
    sample_text = (
        "GOVERNMENT OF INDIA - MINISTRY OF ROAD TRANSPORT\n"
        "Notice Inviting Tender No: NIT/2026/04\n"
        "Bidders must possess a minimum average annual turnover of Rs. 4.5 Crore in the last 3 financial years.\n"
        "The bidder must have at least 4 years of experience in highway paving works.\n"
        "The contractor must have completed at least 2 similar projects of value not less than 2 Crore.\n"
        "Mandatory GST registration certificate and PAN required.\n"
        "Earnest Money Deposit (EMD) of Rs. 10 Lakhs is required via Demand Draft or Bank Guarantee.\n"
    )
    reqs = GeminiRequirementExtractor.fallback_regex_extractor(sample_text)

    assert reqs.minimum_turnover_inr == 45000000.0
    assert reqs.minimum_experience_years == 4
    assert reqs.minimum_similar_projects == 2
    assert reqs.gst_required is True
    assert reqs.emd_amount_inr == 1000000.0
    assert reqs.turnover_clause is not None


def test_matching_engine_eligible_company():
    company = {
        "name": "Apex Infra Works Pvt. Ltd.",
        "business_category": "Road Infrastructure",
        "annual_turnover": 60000000.0,
        "years_of_experience": 5,
        "previous_projects_count": 4,
        "gst_registered": True,
        "gst_number": "27AAAAA0000A1Z5",
        "udyam_registered": True,
        "udyam_number": "UDYAM-MH-01-0012345",
    }
    tender_reqs = {
        "minimum_turnover_inr": 40000000.0,
        "minimum_experience_years": 3,
        "minimum_similar_projects": 2,
        "gst_required": True,
        "emd_amount_inr": 500000.0,
    }
    company_docs = [
        {"document_type": "AUDITED_TURNOVER_PROOF"},
        {"document_type": "EXPERIENCE_CERTIFICATE"},
        {"document_type": "PROJECT_COMPLETION"},
        {"document_type": "GST_CERTIFICATE"},
    ]

    evaluation = EligibilityMatchingEngine.evaluate(company, tender_reqs, company_docs)
    assert evaluation["overall_status"] == "MET"
    assert evaluation["match_score"] == 100.0
    assert len(evaluation["missing_documents"]) == 0


def test_matching_engine_ineligible_turnover():
    company = {
        "name": "Small Infra Works",
        "business_category": "Road Infrastructure",
        "annual_turnover": 10000000.0,  # 1 Crore
        "years_of_experience": 1,
        "previous_projects_count": 0,
        "gst_registered": False,
        "gst_number": None,
        "udyam_registered": False,
    }
    tender_reqs = {
        "minimum_turnover_inr": 50000000.0,  # Requires 5 Crore
        "minimum_experience_years": 3,
        "gst_required": True,
    }
    evaluation = EligibilityMatchingEngine.evaluate(company, tender_reqs, [])
    assert evaluation["overall_status"] == "MISSING"
    assert evaluation["match_score"] < 50.0
    assert "GST Registration Certificate" in evaluation["missing_documents"]


def test_report_generation():
    company = {"name": "Test Company", "business_category": "Civil", "annual_turnover": 50000000.0}
    tender = {"title": "Bridge Construction", "tender_id": "T-101", "estimated_value": 30000000.0}
    eval_res = {
        "overall_status": "MET",
        "match_score": 95.0,
        "criteria": [
            {
                "criterion": "Turnover",
                "status": "MET",
                "required": "₹3 Cr",
                "company_data": "₹5 Cr",
                "reason": "Exceeds requirement",
                "clause_reference": "Clause 4.1",
            }
        ],
        "missing_documents": [],
        "verification_warnings": [],
        "disclaimer": "Sample disclaimer",
    }
    md_report = ReportGenerator.generate_markdown_report(company, tender, eval_res)
    assert "TenderFit – Tender Eligibility Assessment Report" in md_report
    assert "Test Company" in md_report
    assert "Bridge Construction" in md_report
    assert "Clause 4.1" in md_report

