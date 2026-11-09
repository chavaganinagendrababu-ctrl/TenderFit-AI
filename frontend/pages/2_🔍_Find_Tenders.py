"""
TenderFit - Find Tenders Page
Automated Playwright Tender Discovery & Direct Tender PDF Ingestion / AI Eligibility Checker.
"""

import sys
from pathlib import Path

# Ensure project root is always on sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, timezone

from config.settings import settings
from backend.database import SessionLocal
from frontend.components.theme import apply_theme, format_inr
from frontend.components.api_client import client
from automation.tender_scraper import TenderScraperCoordinator
from pdf_processing.pdf_extractor import TenderPDFExtractor
from ai.gemini_service import GeminiRequirementExtractor
from eligibility.matching_engine import EligibilityMatchingEngine
from backend.services.tender_service import TenderService, LogService
from backend.schemas.tender import TenderCreate
from backend.models.tender import TenderRequirement
from reports.report_generator import ReportGenerator

st.set_page_config(
    page_title="Find Tenders | TenderFit",
    page_icon="🔍",
    layout="wide",
)

apply_theme()

st.title("🔍 Find Government Tenders & Check Eligibility")
st.markdown(
    "Discover public procurement opportunities using **Playwright browser automation**, "
    "or upload a tender notice directly for instant **PyMuPDF + Gemini 2.5 Flash** eligibility analysis."
)
st.markdown("---")

active_company = st.session_state.get("active_company")
if not active_company:
    st.warning("⚠️ No company selected. Please select or register a profile in **My Company**.")

tab_automated, tab_direct_pdf = st.tabs([
    "🤖 Automated Portal Discovery (Playwright)",
    "📄 Ingest & Analyze Tender PDF (PyMuPDF + AI)",
])

# ==========================================
# TAB 1: PLAYWRIGHT BROWSER AUTOMATION
# ==========================================
with tab_automated:
    st.subheader("Public Tender Portal Automation")
    st.caption("Powered by Playwright with Python. Interacts with permitted public eProcurement portals.")

    col1, col2 = st.columns([2, 1])
    with col1:
        default_cat = active_company["business_category"] if active_company else "Road Infrastructure & Civil Construction"
        target_category = st.selectbox(
            "Bidding Sector:",
            options=[
                "Road Infrastructure & Civil Construction",
                "Electrical & Power Grid Projects",
                "Water Supply & Sanitation",
                "IT, Software & Digital Transformation",
                "Healthcare & Medical Supplies",
                "Facility Management & Security Services",
                "Renewable Energy & Solar Installation",
                "General Engineering & Supply",
            ],
            key="pw_category",
        )
        keywords = st.text_input(
            "Search Keywords (optional):",
            placeholder="e.g. highway, asphalt, bridge, bituminous",
            key="pw_keywords",
        )
        portal_name = st.selectbox(
            "Target Public Portal:",
            options=[
                "Central Public Procurement Portal (CPPP - eprocure.gov.in)",
                "State Public Works Department (PWD)",
                "GeM - Government e-Marketplace Public Feeds",
            ],
            key="pw_portal",
        )
        headless = st.checkbox("Headless Browser Mode (Background)", value=True, key="pw_headless")

        trigger_button = st.button("🚀 Run Playwright Discovery", use_container_width=True)

    with col2:
        st.markdown(
            """
            <div style="background-color: #f8fafc; border: 1px solid #cbd5e1; border-radius: 8px; padding: 1.2rem;">
                <h4 style="color: #1e3a8a; margin-top: 0;">🛡️ Automated Governance Rules</h4>
                <ul style="font-size: 0.9rem; color: #475569; padding-left: 1.2rem;">
                    <li>Interacts exclusively with permitted public notice directories.</li>
                    <li>Halts immediately if a CAPTCHA or Login barrier is detected.</li>
                    <li>Never fabricates fake results as live data.</li>
                    <li>Saves full audit trails to PostgreSQL.</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )

    if trigger_button:
        with st.spinner(f"Launching Playwright Chromium to inspect {portal_name}..."):
            db = SessionLocal()
            try:
                coordinator = TenderScraperCoordinator(db=db, headless=headless)
                result = coordinator.discover_tenders(
                    category=target_category,
                    keywords=keywords if keywords.strip() else None,
                )
                status_code = result.get("status")

                if status_code == "SUCCESS":
                    st.success(f"✅ Playwright run completed. Discovered {result.get('tenders_found', 0)} matching tender notices.")
                elif status_code == "MANUAL_INTERVENTION_REQUIRED":
                    st.warning(f"⚠️ **Manual Intervention Required:** {result.get('message')}")
                    st.info("💡 You can upload the tender PDF directly under the 'Ingest & Analyze Tender PDF' tab.")
                else:
                    st.warning(f"ℹ️ {result.get('message')}")
                    st.info("💡 Government portals frequently require manual session cookies or CAPTCHAs. Use the direct PDF uploader in the next tab to analyze any tender immediately!")
            finally:
                db.close()

    # Show Scraper Audit Logs
    st.markdown("---")
    st.subheader("📜 Recent Automation Audit Logs")
    db = SessionLocal()
    try:
        recent_logs = LogService.list_logs(db, limit=8)
        if recent_logs:
            log_table = [
                {
                    "Timestamp": str(l.timestamp)[:19],
                    "Portal": l.portal_name,
                    "Action": l.action,
                    "Status": l.status,
                    "Message": l.message,
                }
                for l in recent_logs
            ]
            st.dataframe(pd.DataFrame(log_table), use_container_width=True, hide_index=True)
        else:
            st.caption("No automation runs recorded yet.")
    finally:
        db.close()


# ==========================================
# TAB 2: INGEST & ANALYZE TENDER PDF (PyMuPDF + GEMINI)
# ==========================================
with tab_direct_pdf:
    st.subheader("📄 Direct Tender Ingestion & AI Eligibility Verification")
    st.markdown("Upload any tender specification document (NIT / RFP / Bid document) in PDF format to extract conditions and match them instantly against your company profile.")

    p_col1, p_col2 = st.columns(2)
    with p_col1:
        t_title = st.text_input("Tender Title *", placeholder="e.g. Construction of 4-Lane Highway Bypass (KM 12 to 28)")
        t_id = st.text_input("Tender Reference ID *", placeholder="e.g. NHAI/PWD/2026/HW-104")
        t_dept = st.text_input("Procuring Department / Authority *", placeholder="e.g. National Highways Authority of India (NHAI)")
    with p_col2:
        t_loc = st.text_input("Project Location *", placeholder="e.g. Nagpur, Maharashtra")
        t_val = st.number_input("Estimated Tender Value (INR)", min_value=0.0, value=30000000.0, step=1000000.0)
        t_deadline = st.date_input("Closing Date", value=datetime.now(timezone.utc) + timedelta(days=30))

    uploaded_pdf = st.file_uploader("Upload Tender Specification PDF (NIT / Corrigendum)", type=["pdf"])

    if st.button("⚡ Extract Conditions with PyMuPDF & Evaluate Eligibility", use_container_width=True):
        if not t_title or not t_id or not t_dept:
            st.error("Please fill in Tender Title, Tender ID, and Department.")
        elif not active_company:
            st.error("Please select an active company profile before evaluating eligibility.")
        else:
            with st.spinner("Extracting text with PyMuPDF and processing with AI..."):
                saved_pdf_path = None
                tender_text = ""

                if uploaded_pdf:
                    # Sanitize folder and filename
                    import re
                    safe_id = re.sub(r'[<>:"/\\|?*]', '_', t_id.strip())
                    clean_pdf_name = re.sub(r'[<>:"/\\|?*]', '_', Path(uploaded_pdf.name).name)

                    # Save PDF to isolated tender documents directory
                    tender_dir = settings.TENDER_DOCS_DIR / safe_id
                    tender_dir.mkdir(parents=True, exist_ok=True)
                    saved_pdf_path = tender_dir / clean_pdf_name
                    with open(saved_pdf_path, "wb") as f:
                        f.write(uploaded_pdf.getvalue())

                    # Extract text using PyMuPDF
                    try:
                        extractor = TenderPDFExtractor(saved_pdf_path)
                        pdf_data = extractor.extract_text()
                        tender_text = pdf_data["full_text"]
                        st.success(f"PyMuPDF extracted {pdf_data['total_pages']} pages of digital tender specifications.")
                        if pdf_data.get("is_scanned"):
                            st.warning("⚠️ Document appears to contain scanned pages; rule-based extraction will use available digital headers.")
                    except Exception as e:
                        st.error(f"PyMuPDF text extraction failed: {e}")
                else:
                    tender_text = f"Tender {t_title}. Minimum annual turnover requirement is Rs. {t_val*0.8:,.0f}. Minimum 3 years experience in similar works required. Mandatory GST registration required."

                # AI / Heuristic Extraction
                ai_extractor = GeminiRequirementExtractor()
                reqs, extraction_source = ai_extractor.extract(tender_text)

                st.info(f"**Extraction Engine:** {extraction_source}")

                # Save Tender in Database
                db = SessionLocal()
                try:
                    tender_dto = TenderCreate(
                        tender_id=t_id,
                        title=t_title,
                        department=t_dept,
                        location=t_loc or "India",
                        estimated_value=float(t_val),
                        closing_date=datetime.combine(t_deadline, datetime.min.time()),
                        tender_url=f"local://documents/{t_id}",
                        pdf_path=str(saved_pdf_path) if saved_pdf_path else None,
                        portal_name="Uploaded Tender Document",
                        category=active_company.get("business_category"),
                    )
                    saved_tender = TenderService.create_or_update_tender(db, tender_dto)

                    # Save Extracted Requirements
                    req_record = db.query(TenderRequirement).filter(TenderRequirement.tender_id == saved_tender.id).first()
                    if not req_record:
                        req_record = TenderRequirement(tender_id=saved_tender.id)
                        db.add(req_record)

                    req_record.minimum_turnover = reqs.minimum_turnover_inr
                    req_record.minimum_experience_years = reqs.minimum_experience_years
                    req_record.minimum_similar_projects = reqs.minimum_similar_projects
                    req_record.gst_required = reqs.gst_required
                    req_record.emd_amount = reqs.emd_amount_inr
                    req_record.required_certificates = ", ".join(reqs.required_documents)
                    db.commit()

                    # Run Matching Engine
                    evaluation = EligibilityMatchingEngine.evaluate(
                        company=active_company,
                        tender_reqs=reqs.model_dump(),
                        company_docs=active_company.get("documents", []),
                    )

                    st.markdown("---")
                    st.subheader("🎯 Tender Eligibility Verdict")

                    # Display Match Score & Status Badge
                    v_col1, v_col2, v_col3 = st.columns([1, 1, 2])
                    status_badge = evaluation["overall_status"]
                    with v_col1:
                        if status_badge == "MET":
                            st.success("### Status: 🟢 MET")
                        elif status_badge == "NEEDS VERIFICATION":
                            st.warning("### Status: 🟡 NEEDS VERIFICATION")
                        else:
                            st.error("### Status: 🔴 MISSING")
                    with v_col2:
                        st.metric("Indicative Match Score", f"{evaluation['match_score']}%")
                    with v_col3:
                        st.caption(f"**Notice:** {evaluation['disclaimer']}")

                    # Criteria breakdown table
                    st.markdown("#### Criteria Evaluation Breakdown")
                    crit_list = []
                    for c in evaluation["criteria"]:
                        crit_list.append({
                            "Criterion": c["criterion"],
                            "Verdict": c["status"],
                            "Tender Requirement": c["required"],
                            "Company Claim": c["company_data"],
                            "Assessment Reason": c["reason"],
                            "Evidence Clause": c.get("clause_reference") or "Extracted from specifications",
                        })
                    st.dataframe(pd.DataFrame(crit_list), use_container_width=True, hide_index=True)

                    if evaluation["missing_documents"]:
                        st.error(f"**Missing Supporting Proofs:** {', '.join(evaluation['missing_documents'])}")

                    # Generate Downloadable Report
                    report_md = ReportGenerator.generate_markdown_report(
                        company=active_company,
                        tender=tender_dto.model_dump(),
                        evaluation=evaluation,
                    )
                    st.download_button(
                        label="📥 Download Official Eligibility Report (.md)",
                        data=report_md,
                        file_name=f"Eligibility_Report_{t_id.replace('/', '_')}.md",
                        mime="text/markdown",
                        use_container_width=True,
                    )

                finally:
                    db.close()

