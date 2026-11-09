"""
TenderFit - My Documents Page
Manage and upload statutory certificates, audited financial reports, and project experience proofs.
"""

import streamlit as st
import pandas as pd
from config.settings import settings
from frontend.components.theme import apply_theme
from frontend.components.api_client import client

st.set_page_config(
    page_title="My Documents | TenderFit",
    page_icon="📁",
    layout="wide",
)

apply_theme()

st.title("📁 Company Proof & Statutory Documents")
st.markdown("Upload and manage evidentiary documents required to substantiate company eligibility during tender matching.")
st.markdown("---")

active_company = st.session_state.get("active_company")
if not active_company:
    st.warning("Please select or register a company profile first.")
    st.stop()

col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("📤 Upload New Evidence Document")
    with st.form("doc_upload_form"):
        doc_type = st.selectbox(
            "Document Category *",
            options=[
                "GST Certificate",
                "Udyam / MSME Certificate",
                "PAN Card",
                "Audited Financial Turnover Proof",
                "Experience Certificate",
                "Previous Project Completion Certificate",
                "ISO / Technical Qualification",
                "Power of Attorney",
                "Bank Solvency Certificate",
            ],
        )
        file = st.file_uploader("Select PDF or Scanned Document *", type=["pdf", "png", "jpg", "jpeg"])
        submit_btn = st.form_submit_button("Upload & Attach to Profile", use_container_width=True)

        if submit_btn:
            if not file:
                st.error("Please choose a file to upload.")
            else:
                try:
                    res = client.upload_document(
                        company_id=active_company["id"],
                        document_type=doc_type,
                        file_name=file.name,
                        file_bytes=file.getvalue(),
                    )
                    st.success(f"✅ Successfully attached '{file.name}' as '{doc_type}'!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Upload error: {e}")

with col2:
    st.subheader(f"📑 Document Repository ({active_company['name']})")
    
    # Reload company data to reflect latest docs
    fresh_comp = client.get_company(active_company["id"])
    docs = fresh_comp.get("documents", []) if fresh_comp else []

    if not docs:
        st.info("No documents uploaded yet for this enterprise. Upload proofs on the left to verify your tender eligibility.")
    else:
        table_rows = []
        for d in docs:
            table_rows.append({
                "Doc ID": d["id"],
                "Document Type": d["document_type"],
                "File Name": d["file_name"],
                "Size (KB)": round(d["file_size_bytes"] / 1024, 1),
                "Uploaded At": d["uploaded_at"][:19],
            })
        st.dataframe(pd.DataFrame(table_rows), use_container_width=True, hide_index=True)

st.markdown("---")
st.caption("🔒 **Security & Privacy:** Uploaded documents are stored locally in an isolated repository and accessed strictly for internal eligibility validation.")

