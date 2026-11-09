"""
TenderFit - Seed Data Script
Populates the database with realistic registered companies, sample tenders,
and eligibility criteria so the application is immediately testable upon launch.
"""

from datetime import datetime, timedelta
from backend.database import SessionLocal, init_db
from backend.models.company import Company, CompanyDocument
from backend.models.tender import Tender, TenderRequirement
from backend.models.log import AutomationLog


def seed():
    init_db()
    db = SessionLocal()

    try:
        # 1. Seed Company Profile
        existing_company = db.query(Company).filter(Company.name == "Apex Infrastructure Projects Pvt. Ltd.").first()
        if not existing_company:
            company = Company(
                name="Apex Infrastructure Projects Pvt. Ltd.",
                business_category="Road Infrastructure & Civil Construction",
                location="Mumbai, Maharashtra",
                annual_turnover=65000000.0,  # 6.5 Crores
                years_of_experience=6,
                previous_projects_count=12,
                gst_registered=True,
                gst_number="27AAAAA0000A1Z5",
                udyam_registered=True,
                udyam_number="UDYAM-MH-01-0098765",
                specialisations="Highway widening, bituminous macadam paving, RCC culverts & bridges, CPWD Class-I certified.",
            )
            db.add(company)
            db.commit()
            db.refresh(company)

            # Add sample document records
            doc1 = CompanyDocument(
                company_id=company.id,
                document_type="GST_CERTIFICATE",
                file_name="GST_Registration_Certificate_2024.pdf",
                file_path="documents/company_documents/GST_Registration_Certificate_2024.pdf",
                file_size_bytes=245800,
            )
            doc2 = CompanyDocument(
                company_id=company.id,
                document_type="AUDITED_TURNOVER_PROOF",
                file_name="Audited_Financial_Statement_FY23_24.pdf",
                file_path="documents/company_documents/Audited_Financial_Statement_FY23_24.pdf",
                file_size_bytes=1048576,
            )
            doc3 = CompanyDocument(
                company_id=company.id,
                document_type="UDYAM_MSME_CERTIFICATE",
                file_name="Udyam_Registration_Certificate.pdf",
                file_path="documents/company_documents/Udyam_Registration_Certificate.pdf",
                file_size_bytes=182400,
            )
            db.add_all([doc1, doc2, doc3])
            db.commit()
            print("Seeded sample company: 'Apex Infrastructure Projects Pvt. Ltd.' with 3 documents.")

        # 2. Seed Realistic Public Tenders
        tenders_data = [
            {
                "tender_id": "NHAI-PWD-2026-HW-089",
                "title": "Widening & Strengthening of 4-Lane State Highway (KM 14 to 32)",
                "department": "Public Works Department (PWD), Maharashtra",
                "location": "Pune - Solapur Highway, Maharashtra",
                "estimated_value": 45000000.0,  # 4.5 Crores
                "closing_date": datetime.utcnow() + timedelta(days=24),
                "tender_url": "https://eprocure.gov.in/eprocure/app?page=FrontEndTenderDetails&service=page&tenderId=89234",
                "portal_name": "Central Public Procurement Portal (CPPP)",
                "category": "Road Infrastructure & Civil Construction",
                "req": {
                    "minimum_turnover": 40000000.0,  # 4.0 Crores
                    "minimum_experience_years": 4,
                    "minimum_similar_projects": 2,
                    "gst_required": True,
                    "emd_amount": 900000.0,
                    "required_certificates": "Class-I PWD Contractor, ISO 9001:2015, Audited Balance Sheet",
                    "technical_qualifications": "Experience in Dense Bituminous Macadam (DBM) laying over 15 KM.",
                },
            },
            {
                "tender_id": "CPWD-DEL-CIVIL-2026-042",
                "title": "Construction of Multi-Level Automated Parking Facility and Access Roads",
                "department": "Central Public Works Department (CPWD)",
                "location": "New Delhi, Delhi",
                "estimated_value": 85000000.0,  # 8.5 Crores
                "closing_date": datetime.utcnow() + timedelta(days=14),
                "tender_url": "https://eprocure.gov.in/eprocure/app?page=FrontEndTenderDetails&service=page&tenderId=89912",
                "portal_name": "Central Public Procurement Portal (CPPP)",
                "category": "Road Infrastructure & Civil Construction",
                "req": {
                    "minimum_turnover": 75000000.0,  # 7.5 Crores (Will test MISSING turnover for 6.5 Cr company)
                    "minimum_experience_years": 5,
                    "minimum_similar_projects": 3,
                    "gst_required": True,
                    "emd_amount": 1700000.0,
                    "required_certificates": "CPWD Enlistment Class A, Valid GSTIN",
                },
            },
            {
                "tender_id": "MCD-MUM-ROAD-2026-118",
                "title": "Annual Maintenance & Resurfacing of Municipal Arterial Roads Zone 4",
                "department": "Brihanmumbai Municipal Corporation (BMC)",
                "location": "Mumbai, Maharashtra",
                "estimated_value": 28000000.0,  # 2.8 Crores
                "closing_date": datetime.utcnow() + timedelta(days=32),
                "tender_url": "https://portal.mcgm.gov.in/irj/portal/anonymous/qleproc",
                "portal_name": "Municipal Public Tender Portal",
                "category": "Road Infrastructure & Civil Construction",
                "req": {
                    "minimum_turnover": 20000000.0,  # 2.0 Crores
                    "minimum_experience_years": 3,
                    "minimum_similar_projects": 1,
                    "gst_required": True,
                    "emd_amount": 560000.0,
                    "required_certificates": "BMC Registered Contractor, Active GST",
                },
            },
        ]

        for item in tenders_data:
            req_info = item.pop("req")
            existing = db.query(Tender).filter(Tender.tender_id == item["tender_id"]).first()
            if not existing:
                t = Tender(**item)
                db.add(t)
                db.commit()
                db.refresh(t)

                treq = TenderRequirement(
                    tender_id=t.id,
                    minimum_turnover=req_info.get("minimum_turnover"),
                    minimum_experience_years=req_info.get("minimum_experience_years"),
                    minimum_similar_projects=req_info.get("minimum_similar_projects"),
                    gst_required=req_info.get("gst_required", True),
                    emd_amount=req_info.get("emd_amount"),
                    required_certificates=req_info.get("required_certificates"),
                    technical_qualifications=req_info.get("technical_qualifications"),
                )
                db.add(treq)
                db.commit()

        # 3. Seed an initial audit log
        log_entry = AutomationLog(
            portal_name="Central Public Procurement Portal (CPPP)",
            action="SYSTEM_INIT",
            status="SUCCESS",
            message="TenderFit database initialized. Ready for tender ingestion and AI eligibility verification.",
        )
        db.add(log_entry)
        db.commit()
        print("Seeded 3 realistic public government tenders with structured requirements.")

    finally:
        db.close()


if __name__ == "__main__":
    seed()

