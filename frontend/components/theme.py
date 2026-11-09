"""
TenderFit - Theme and Custom Styling
Provides clean, professional SaaS CSS styling with navy blue, white, and blue accents.
"""

import streamlit as st


def apply_theme():
    """Applies modern SaaS styling to the Streamlit app."""
    custom_css = """
    <style>
    /* Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* Primary Navy Header */
    .tenderfit-header {
        background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 100%);
        padding: 1.8rem 2rem;
        border-radius: 12px;
        color: #ffffff;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }

    .tenderfit-header h1 {
        color: #ffffff !important;
        font-weight: 700;
        font-size: 2.2rem;
        margin: 0;
        letter-spacing: -0.5px;
    }

    .tenderfit-header p {
        color: #93c5fd !important;
        font-size: 1.05rem;
        margin: 0.4rem 0 0 0;
        font-weight: 500;
    }

    /* Metric Cards */
    .metric-card {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 1.2rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }

    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(30, 58, 138, 0.08);
    }

    .metric-title {
        color: #64748b;
        font-size: 0.85rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    .metric-value {
        color: #0f172a;
        font-size: 1.8rem;
        font-weight: 700;
        margin-top: 0.2rem;
    }

    /* Status Badges */
    .badge-met {
        background-color: #dcfce7;
        color: #15803d;
        padding: 0.25rem 0.65rem;
        border-radius: 9999px;
        font-weight: 600;
        font-size: 0.8rem;
        display: inline-block;
    }

    .badge-missing {
        background-color: #fee2e2;
        color: #b91c1c;
        padding: 0.25rem 0.65rem;
        border-radius: 9999px;
        font-weight: 600;
        font-size: 0.8rem;
        display: inline-block;
    }

    .badge-verify {
        background-color: #fef3c7;
        color: #b45309;
        padding: 0.25rem 0.65rem;
        border-radius: 9999px;
        font-weight: 600;
        font-size: 0.8rem;
        display: inline-block;
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #f8fafc;
        border-right: 1px solid #e2e8f0;
    }

    /* Primary Buttons */
    .stButton > button {
        background-color: #1e40af;
        color: white;
        border-radius: 8px;
        font-weight: 600;
        border: none;
        padding: 0.5rem 1.25rem;
        transition: background-color 0.2s ease;
    }

    .stButton > button:hover {
        background-color: #1d4ed8;
        color: white;
    }
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)


def format_inr(amount: float) -> str:
    """Formats an amount in INR with Crores / Lakhs representation."""
    if amount is None or amount == 0:
        return "₹0"
    if amount >= 10_000_000:
        cr = amount / 10_000_000
        return f"₹{cr:.2f} Cr"
    elif amount >= 100_000:
        lakhs = amount / 100_000
        return f"₹{lakhs:.2f} Lakhs"
    else:
        return f"₹{amount:,.0f}"

