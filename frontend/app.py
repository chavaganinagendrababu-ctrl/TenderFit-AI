"""
TenderFit - Streamlit Main Application & Executive Dashboard
Tagline: Find. Match. Win.
"""

import sys
from pathlib import Path

# Ensure project root is always on sys.path regardless of execution directory
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import streamlit as st
import pandas as pd
from datetime import datetime

from config.settings import settings
from backend.database import init_db, ACTIVE_DIALECT
from frontend.components.theme import apply_theme, format_inr
from frontend.components.api_client import client

# Ensure database tables exist
init_db()

# Streamlit Page Config
st.set_page_config(
    page_title=f"{settings.APP_NAME} | AI Government Tender Discovery & Eligibility",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_theme()

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("## 🏛️ **TenderFit**")
    st.caption("AI-Powered Government Tender Discovery & Eligibility Checker")
    st.markdown("---")

    # Company Selector
    companies = client.list_companies()
    if companies:
        company_options = {c["name"]: c["id"] for c in companies}
        selected_company_name = st.selectbox(
            "Active Enterprise Profile:",
            options=list(company_options.keys()),
            key="active_company_name"
        )
        selected_company_id = company_options[selected_company_name]
        active_company = client.get_company(selected_company_id)
        st.session_state["active_company"] = active_company
    else:
        st.warning("No company registered yet.")
        active_company = None
        st.session_state["active_company"] = None

    st.markdown("---")
    st.markdown("### Navigation")
    st.markdown(
        """
        - 🏠 **[Dashboard](/)**
        - 🏢 **[My Company](/My_Company)**
        - 🔍 **[Find Tenders](/Find_Tenders)**
        - 📁 **[My Documents](/My_Documents)**
        - 📊 **[Eligibility Reports](/Eligibility_Reports)**
        - ⚙️ **[Settings](/Settings)**
        """
    )
    st.markdown("---")
    
    # System Status Indicator
    backend_status = client.is_backend_online()
    st.caption(f"**Database:** {ACTIVE_DIALECT.upper()}")
    st.caption(f"**API Status:** {'🟢 Online' if backend_status else '🟡 Direct DB Mode'}")
    st.caption("Version 1.0.0 (Milestone 1)")


# --- HEADER ---
st.markdown(
    f"""
    <div class="tenderfit-header">
        <h1>{settings.APP_NAME}</h1>
        <p>{settings.APP_TAGLINE} &nbsp;|&nbsp; Discover high-value government contracts & verify eligibility instantly</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# --- COMPANY CONTEXT BANNER ---
if active_company:
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-title">Active Company</div>
                <div class="metric-value" style="font-size: 1.25rem;">{active_company['name']}</div>
                <small style="color: #64748b;">📍 {active_company['location']}</small>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-title">Primary Sector</div>
                <div class="metric-value" style="font-size: 1.25rem;">{active_company['business_category']}</div>
                <small style="color: #64748b;">Experience: {active_company['years_of_experience']} Years</small>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col3:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-title">Annual Turnover</div>
                <div class="metric-value" style="font-size: 1.25rem;">{format_inr(active_company['annual_turnover'])}</div>
                <small style="color: #64748b;">Completed: {active_company['previous_projects_count']} Projects</small>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col4:
        gst_status = "✅ Active GST" if active_company["gst_registered"] else "❌ No GST"
        msme_status = "✅ MSME" if active_company["udyam_registered"] else "❌ Non-MSME"
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-title">Statutory Status</div>
                <div class="metric-value" style="font-size: 1.1rem; padding-top: 0.2rem;">{gst_status}</div>
                <small style="color: #64748b;">{msme_status} &nbsp;|&nbsp; {len(active_company.get('documents', []))} Docs Uploaded</small>
            </div>
            """,
            unsafe_allow_html=True,
        )
else:
    st.info(
        "👋 Welcome to TenderFit! You don't have a registered company profile yet. "
        "Please visit **[My Company](/My_Company)** to set up your business details."
    )

st.markdown("<br>", unsafe_allow_html=True)

# --- KEY PERFORMANCE METRICS ---
st.subheader("📈 Tender Pipeline Overview")

m_col1, m_col2, m_col3, m_col4, m_col5 = st.columns(5)

# Fetch current tenders
current_category = active_company["business_category"] if active_company else None
tenders = client.list_tenders()

total_tenders = len(tenders)
relevant_tenders = len([t for t in tenders if current_category and current_category.lower() in (t.get("category") or "").lower()]) if current_category else total_tenders

with m_col1:
    st.metric("Total Discovered", f"{total_tenders}")
with m_col2:
    st.metric("Relevant Sector", f"{relevant_tenders}")
with m_col3:
    st.metric("Strong Matches", "0", help="Tenders meeting 100% of turnover and experience conditions")
with m_col4:
    st.metric("Partial Matches", "0", help="Tenders meeting primary requirements but missing optional proofs")
with m_col5:
    st.metric("Needing Attention", "0", help="Tenders requiring immediate document verification")

st.markdown("---")

# --- TENDER LISTING TABLE & DETAILS ---
st.subheader("📋 Discovered Government Opportunities")

if not tenders:
    st.markdown(
        """
        <div style="text-align: center; padding: 2.5rem; background: #f8fafc; border: 1px dashed #cbd5e1; border-radius: 8px;">
            <h4 style="color: #475569; margin-bottom: 0.5rem;">No Government Tenders Discovered Yet</h4>
            <p style="color: #64748b; font-size: 0.95rem;">
                Run the <strong>Playwright Browser Automation</strong> in <strong>Tender Search</strong> to ingest live opportunities from permitted public portals.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
else:
    # Display table of discovered tenders
    table_data = []
    for t in tenders:
        table_data.append({
            "Tender ID": t["tender_id"],
            "Title": t["title"],
            "Department": t["department"],
            "Location": t["location"],
            "Est. Value": format_inr(t["estimated_value"]),
            "Closing Date": t["closing_date"][:10] if t["closing_date"] else "Open",
            "Portal": t["portal_name"],
        })

    df = pd.DataFrame(table_data)
    st.dataframe(df, use_container_width=True, hide_index=True)

    # Tender Details Expander
    st.markdown("### 🔎 Tender Detail & Eligibility Inspector")
    selected_tender_id = st.selectbox("Select Tender to Inspect:", options=[t["tender_id"] for t in tenders])
    selected_tender = next((t for t in tenders if t["tender_id"] == selected_tender_id), None)

    if selected_tender:
        t_col1, t_col2 = st.columns([2, 1])
        with t_col1:
            st.markdown(f"#### {selected_tender['title']}")
            st.markdown(f"**Department:** {selected_tender['department']}")
            st.markdown(f"**Location:** {selected_tender['location']}")
            st.markdown(f"**Source Portal:** {selected_tender['portal_name']}")
            st.markdown(f"**Portal URL:** [{selected_tender['tender_url']}]({selected_tender['tender_url']})")
        with t_col2:
            st.markdown(
                f"""
                <div style="background: #f1f5f9; padding: 1rem; border-radius: 8px;">
                    <div style="font-size: 0.85rem; color: #64748b;">ESTIMATED VALUE</div>
                    <div style="font-size: 1.5rem; font-weight: 700; color: #1e3a8a;">{format_inr(selected_tender['estimated_value'])}</div>
                    <div style="font-size: 0.85rem; color: #64748b; margin-top: 0.5rem;">CLOSING DEADLINE</div>
                    <div style="font-size: 1.1rem; font-weight: 600; color: #b91c1c;">{selected_tender['closing_date']}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.info("💡 Eligibility requirement extraction and matching will run automatically as documents are processed in upcoming modules.")

