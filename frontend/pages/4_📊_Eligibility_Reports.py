"""
TenderFit - Eligibility Reports Page
Generate, inspect, and export comprehensive audit-ready eligibility reports.
"""

import sys
from pathlib import Path

# Ensure project root is always on sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import streamlit as st
import pandas as pd
from config.settings import settings
from backend.database import SessionLocal
from backend.models.tender import Tender, TenderRequirement
from frontend.components.theme import apply_theme, format_inr
from frontend.components.api_client import client
from eligibility.matching_engine import EligibilityMatchingEngine
from reports.report_generator import ReportGenerator

st.set_page_config(
    page_title="Eligibility Reports | TenderFit",
    page_icon="📊",
    layout="wide",
)

apply_theme()

st.title("📊 Eligibility Reports & Compliance Audit")
st.markdown("Inspect comprehensive eligibility assessments comparing your company credentials against discovered tenders.")
st.markdown("---")

active_company = st.session_state.get("active_company")
if not active_company:
    st.warning("⚠️ Please select an active company profile in the sidebar or under **My Company**.")
    st.stop()

# Query available tenders with requirements
db = SessionLocal()
try:
    tenders = db.query(Tender).all()
    if not tenders:
        st.info("No tenders available for report generation yet. Navigate to **Find Tenders** to ingest or discover opportunities.")
        st.stop()

    tender_choices = {f"{t.tender_id} - {t.title[:50]}...": t for t in tenders}
    selected_choice = st.selectbox("Select Tender for Eligibility Evaluation:", options=list(tender_choices.keys()))
    target_tender = tender_choices[selected_choice]

    # Check for requirements
    req_record = db.query(TenderRequirement).filter(TenderRequirement.tender_id == target_tender.id).first()
    
    tender_reqs = {}
    if req_record:
        tender_reqs = {
            "minimum_turnover_inr": req_record.minimum_turnover,
            "minimum_experience_years": req_record.minimum_experience_years,
            "minimum_similar_projects": req_record.minimum_similar_projects,
            "gst_required": req_record.gst_required,
            "emd_amount_inr": req_record.emd_amount,
            "turnover_clause": f"Minimum turnover condition for {target_tender.title}",
        }
    else:
        # Defaults based on estimated value
        tender_reqs = {
            "minimum_turnover_inr": (target_tender.estimated_value or 10000000.0) * 0.7,
            "minimum_experience_years": 3,
            "minimum_similar_projects": 2,
            "gst_required": True,
            "emd_amount_inr": (target_tender.estimated_value or 10000000.0) * 0.02,
        }

    # Evaluate
    evaluation = EligibilityMatchingEngine.evaluate(
        company=active_company,
        tender_reqs=tender_reqs,
        company_docs=active_company.get("documents", []),
    )

    # Display Report Header Cards
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-title">Active Company</div>
                <div class="metric-value" style="font-size: 1.3rem;">{active_company['name']}</div>
                <small style="color: #64748b;">📍 {active_company['location']}</small>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-title">Tender Value</div>
                <div class="metric-value" style="font-size: 1.3rem;">{format_inr(target_tender.estimated_value)}</div>
                <small style="color: #64748b;">ID: {target_tender.tender_id}</small>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col3:
        status = evaluation["overall_status"]
        status_color = "#15803d" if status == "MET" else ("#b45309" if status == "NEEDS VERIFICATION" else "#b91c1c")
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-title">Eligibility Outcome</div>
                <div class="metric-value" style="font-size: 1.3rem; color: {status_color};">{status}</div>
                <small style="color: #64748b;">Match Score: {evaluation['match_score']}%</small>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("📋 Evaluation Criteria Matrix")

    matrix_rows = []
    for c in evaluation["criteria"]:
        matrix_rows.append({
            "Criterion": c["criterion"],
            "Verdict": c["status"],
            "Required": c["required"],
            "Company Evidence": c["company_data"],
            "Rationale": c["reason"],
            "Clause Reference": c["clause_reference"],
        })
    st.dataframe(pd.DataFrame(matrix_rows), use_container_width=True, hide_index=True)

    if evaluation["missing_documents"]:
        st.error(f"**Missing Evidentiary Documents:** {', '.join(evaluation['missing_documents'])}")

    if evaluation["verification_warnings"]:
        st.warning(f"**Action Items:** {', '.join(evaluation['verification_warnings'])}")

    st.markdown("---")
    
    # Download Button
    tender_dict = {
        "title": target_tender.title,
        "tender_id": target_tender.tender_id,
        "department": target_tender.department,
        "location": target_tender.location,
        "estimated_value": target_tender.estimated_value,
        "closing_date": str(target_tender.closing_date),
        "portal_name": target_tender.portal_name,
        "tender_url": target_tender.tender_url,
    }
    report_content = ReportGenerator.generate_markdown_report(
        company=active_company,
        tender=tender_dict,
        evaluation=evaluation,
    )

    st.download_button(
        label="📥 Download Official Eligibility Report (.md)",
        data=report_content,
        file_name=f"TenderFit_Report_{target_tender.tender_id.replace('/', '_')}.md",
        mime="text/markdown",
        use_container_width=True,
    )

finally:
    db.close()

