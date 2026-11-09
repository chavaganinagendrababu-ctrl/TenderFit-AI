"""
TenderFit - Company Profile and Registration Page
Allows companies to register, update profile attributes, and upload statutory & financial proof documents.
"""

import streamlit as st
from config.settings import settings
from frontend.components.theme import apply_theme, format_inr
from frontend.components.api_client import client

st.set_page_config(
    page_title="My Company Profile | TenderFit",
    page_icon="🏢",
    layout="wide",
)

apply_theme()

st.title("🏢 Company Registration & Profile Management")
st.markdown(
    "Register your company details and upload supporting documents. "
    "TenderFit will match these credentials against public government tender eligibility criteria."
)
st.markdown("---")

tab_register, tab_view = st.tabs(["📝 Register New Company", "📋 Existing Profiles & Documents"])

# --- TAB 1: REGISTRATION FORM ---
with tab_register:
    st.subheader("Enterprise Information")
    with st.form("company_registration_form"):
        col1, col2 = st.columns(2)

        with col1:
            name = st.text_input(
                "Company Name *",
                placeholder="e.g. Apex Infra Projects Pvt. Ltd.",
                help="Official registered legal name of the bidding enterprise.",
            )
            business_category = st.selectbox(
                "Primary Business Category *",
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
                help="Sector in which the company actively tenders.",
            )
            location = st.text_input(
                "Company Headquarters Location *",
                placeholder="e.g. Mumbai, Maharashtra",
                help="City, State of operational headquarters.",
            )
            annual_turnover = st.number_input(
                "Annual Turnover (INR) *",
                min_value=0.0,
                step=1000000.0,
                format="%.2f",
                help="Average audited turnover of the last 3 financial years (e.g. 50000000 for 5 Crore).",
            )
            if annual_turnover > 0:
                st.caption(f"Formatted: **{format_inr(annual_turnover)}**")

        with col2:
            years_of_experience = st.number_input(
                "Years of Operational Experience *",
                min_value=0,
                max_value=100,
                value=3,
                step=1,
            )
            previous_projects_count = st.number_input(
                "Successfully Completed Projects *",
                min_value=0,
                max_value=10000,
                value=5,
                step=1,
            )
            st.markdown("#### Statutory Registrations")
            gst_registered = st.checkbox("GST Registered", value=True)
            gst_number = st.text_input(
                "GSTIN (15 Digits)",
                placeholder="e.g. 27AAAAA0000A1Z5",
                disabled=not gst_registered,
            )

            udyam_registered = st.checkbox("Udyam / MSME Registered", value=True)
            udyam_number = st.text_input(
                "Udyam Registration Number",
                placeholder="e.g. UDYAM-MH-01-0012345",
                disabled=not udyam_registered,
            )

        specialisations = st.text_area(
            "Core Specialisations & Machinery/Technical Capabilities",
            placeholder="e.g. Highway construction, bitumin mixing plant, automated pavers, ISO 9001:2015 certified, class-1 contractor with CPWD.",
            help="Detail technical strengths, equipment owned, and specific contractor classifications.",
        )

        submitted = st.form_submit_button("💾 Save Company Profile", use_container_width=True)

        if submitted:
            if not name.strip():
                st.error("Company Name is required.")
            elif not location.strip():
                st.error("Location is required.")
            else:
                payload = {
                    "name": name.strip(),
                    "business_category": business_category,
                    "location": location.strip(),
                    "annual_turnover": float(annual_turnover),
                    "years_of_experience": int(years_of_experience),
                    "previous_projects_count": int(previous_projects_count),
                    "gst_registered": gst_registered,
                    "gst_number": gst_number.strip() if (gst_registered and gst_number) else None,
                    "udyam_registered": udyam_registered,
                    "udyam_number": udyam_number.strip() if (udyam_registered and udyam_number) else None,
                    "specialisations": specialisations.strip() if specialisations else None,
                }
                try:
                    res = client.register_company(payload)
                    st.success(f"🎉 Company '{name}' registered successfully in PostgreSQL! (ID: {res.get('id')})")
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to register company: {e}")

# --- TAB 2: EXISTING PROFILES & SUPPORTING DOCUMENTS ---
with tab_view:
    companies = client.list_companies()
    if not companies:
        st.info("No companies registered yet. Use the 'Register New Company' tab to add your first profile.")
    else:
        st.subheader("Registered Companies")
        selected_comp_name = st.selectbox(
            "Select Company to view / attach documents:",
            options=[c["name"] for c in companies],
            key="manage_selected_comp",
        )
        comp = next((c for c in companies if c["name"] == selected_comp_name), None)

        if comp:
            v_col1, v_col2 = st.columns([2, 1])
            with v_col1:
                st.markdown(f"### **{comp['name']}**")
                st.markdown(f"**Sector:** {comp['business_category']} &nbsp;|&nbsp; **Location:** {comp['location']}")
                st.markdown(f"**Annual Turnover:** {format_inr(comp['annual_turnover'])}")
                st.markdown(f"**Experience:** {comp['years_of_experience']} Years &nbsp;|&nbsp; **Projects Completed:** {comp['previous_projects_count']}")
                st.markdown(f"**GSTIN:** `{comp['gst_number'] or 'Not provided'}` &nbsp;|&nbsp; **Udyam:** `{comp['udyam_number'] or 'Not provided'}`")
                if comp.get("specialisations"):
                    st.markdown(f"**Capabilities:** {comp['specialisations']}")

            with v_col2:
                st.markdown("#### 📤 Upload Supporting Document")
                with st.form(f"upload_doc_form_{comp['id']}"):
                    doc_type = st.selectbox(
                        "Document Type:",
                        options=[
                            "GST Certificate",
                            "Udyam / MSME Certificate",
                            "PAN Card",
                            "Audited Financial Turnover Proof",
                            "Experience Certificate",
                            "Previous Project Completion Certificate",
                            "ISO / Technical Qualification",
                        ],
                    )
                    uploaded_file = st.file_uploader("Select PDF or Image", type=["pdf", "png", "jpg", "jpeg"])
                    upload_btn = st.form_submit_button("Upload Document")

                    if upload_btn:
                        if not uploaded_file:
                            st.error("Please select a file to upload.")
                        else:
                            try:
                                client.upload_document(
                                    company_id=comp["id"],
                                    document_type=doc_type,
                                    file_name=uploaded_file.name,
                                    file_bytes=uploaded_file.getvalue(),
                                )
                                st.success(f"Attached '{uploaded_file.name}' to {comp['name']}.")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Upload failed: {e}")

            # Uploaded Documents Table
            st.markdown("---")
            st.subheader("📑 Uploaded Supporting Documents")
            docs = comp.get("documents", [])
            if not docs:
                st.caption("No documents uploaded yet. Upload proofs above to support eligibility verification.")
            else:
                doc_list = []
                for d in docs:
                    doc_list.append({
                        "Document ID": d["id"],
                        "Type": d["document_type"],
                        "File Name": d["file_name"],
                        "Size (KB)": round(d["file_size_bytes"] / 1024, 2),
                        "Uploaded At": d["uploaded_at"][:19],
                    })
                st.table(doc_list)

