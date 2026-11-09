"""
TenderFit - Settings and Diagnostics Page
Configure API URLs, verify database connections, and test browser automation status.
"""

import streamlit as st
from config.settings import settings
from backend.database import ACTIVE_DIALECT, engine
from frontend.components.theme import apply_theme
from frontend.components.api_client import client

st.set_page_config(
    page_title="Settings & System Diagnostics | TenderFit",
    page_icon="⚙️",
    layout="wide",
)

apply_theme()

st.title("⚙️ System Configuration & Diagnostics")
st.markdown("Inspect backend health, active database dialect, and storage paths.")
st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Database Connectivity")
    st.write(f"**Target URL:** `{settings.DATABASE_URL}`")
    st.write(f"**Active Dialect:** `{ACTIVE_DIALECT.upper()}`")
    
    if ACTIVE_DIALECT == "postgresql":
        st.success("Connected to live PostgreSQL database!")
    else:
        st.warning(
            "Using SQLite fallback. To switch to PostgreSQL, ensure your local PostgreSQL server "
            "is running and check the `DATABASE_URL` in `.env`."
        )

    st.markdown("---")
    st.subheader("Backend API")
    backend_live = client.is_backend_online()
    st.write(f"**API Base URL:** `{settings.API_BASE_URL}`")
    st.write(f"**Status:** {'🟢 Online' if backend_live else '🟡 Offline / Direct DB mode active'}")

with col2:
    st.subheader("Storage Directories")
    st.write(f"**Company Documents:** `{settings.COMPANY_DOCS_DIR}`")
    st.write(f"**Tender Documents:** `{settings.TENDER_DOCS_DIR}`")
    st.write(f"**Reports:** `{settings.REPORTS_DIR}`")

    st.markdown("---")
    st.subheader("Playwright Configuration")
    st.write(f"**Headless Default:** `{settings.PLAYWRIGHT_HEADLESS}`")
    st.write(f"**Navigation Timeout:** `{settings.PLAYWRIGHT_TIMEOUT} ms`")

