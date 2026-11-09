"""
TenderFit - Gemini AI Requirement Extraction Service
Uses Gemini 2.5 Flash to parse unstructured tender text into strict validated schemas.
Preserves original clauses for evidence and provides rule-based prefill fallback.
"""

import json
import re
import logging
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field

from config.settings import settings

logger = logging.getLogger("tenderfit.ai")


class ExtractedTenderRequirements(BaseModel):
    minimum_turnover_inr: Optional[float] = Field(None, description="Minimum annual turnover in INR required")
    minimum_experience_years: Optional[int] = Field(None, description="Minimum operational experience in years")
    minimum_similar_projects: Optional[int] = Field(None, description="Minimum number of similar completed works")
    gst_required: bool = Field(True, description="Whether active GSTIN registration is mandatory")
    emd_amount_inr: Optional[float] = Field(None, description="Earnest Money Deposit in INR")
    required_documents: List[str] = Field(default_factory=list, description="List of required certificates/documents")
    technical_qualifications: List[str] = Field(default_factory=list, description="List of technical criteria")
    submission_deadline: Optional[str] = Field(None, description="Closing date and time string")

    # Audit clause references
    turnover_clause: Optional[str] = Field(None, description="Exact tender clause for turnover requirement")
    experience_clause: Optional[str] = Field(None, description="Exact tender clause for experience")
    similar_projects_clause: Optional[str] = Field(None, description="Exact clause for previous projects")
    gst_clause: Optional[str] = Field(None, description="Exact clause mentioning GST")
    emd_clause: Optional[str] = Field(None, description="Exact clause mentioning EMD")
    documents_clause: Optional[str] = Field(None, description="Exact clause listing mandatory documents")


class GeminiRequirementExtractor:
    """
    Extracts eligibility criteria using Gemini 2.5 Flash.
    Validates output using Pydantic, preserves verbatim clauses,
    and falls back to rule-based heuristics if no API key is provided.
    """

    def __init__(self, api_key: Optional[str] = None, model_name: Optional[str] = None):
        self.api_key = api_key or settings.GEMINI_API_KEY
        self.model_name = model_name or settings.GEMINI_MODEL

    def is_configured(self) -> bool:
        return bool(self.api_key and len(self.api_key.strip()) > 5)

    def extract_with_gemini(self, tender_text: str) -> Optional[ExtractedTenderRequirements]:
        """Invokes Gemini 2.5 Flash with structured JSON output instructions."""
        if not self.is_configured():
            return None

        try:
            from google import genai
            from google.genai import types

            client = genai.Client(api_key=self.api_key)
            prompt = (
                "You are an expert Government Procurement and Legal Tender Analyst.\n"
                "Extract the verifiable eligibility criteria from the tender text into JSON.\n\n"
                "CRITICAL RULES:\n"
                "1. NEVER invent requirements. If not stated, use null.\n"
                "2. For each requirement, include the exact verbatim sentence from the text as the clause evidence.\n\n"
                f"Tender Document Text:\n{tender_text[:25000]}\n"
            )

            response = client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=ExtractedTenderRequirements,
                ),
            )

            if response and response.text:
                parsed = json.loads(response.text)
                return ExtractedTenderRequirements(**parsed)
        except Exception as e:
            logger.error(f"Gemini API call failed: {e}", exc_info=True)
            return None

    @staticmethod
    def fallback_regex_extractor(tender_text: str) -> ExtractedTenderRequirements:
        """
        Rule-based heuristic extractor used when Gemini is unconfigured or offline.
        Inspects text for common government procurement keywords and figures.
        """
        text_lower = tender_text.lower()

        # 1. Turnover heuristic (e.g., turnover of Rs. 4.5 Crore / 30 Lakhs / 30,00,000)
        turnover_inr = None
        turnover_clause = None
        turnover_match = re.search(r'(?:annual\s+turnover|turnover)\s*(?:of|is|:)?\s*(?:rs\.?|inr|₹)?\s*([\d,.]+)\s*(crore|cr|lakh|lakhs)?', text_lower)
        if not turnover_match:
            turnover_match = re.search(r'(?:annual\s+turnover|turnover)[^\n]{1,40}?(?:rs\.?|inr|₹)?\s*([\d,.]+)\s*(crore|cr|lakh|lakhs)?', text_lower)

        if turnover_match:
            try:
                val_str = turnover_match.group(1).replace(",", "")
                val = float(val_str)
                unit = (turnover_match.group(2) or "").lower()
                if "cr" in unit:
                    val *= 10_000_000
                elif "lakh" in unit:
                    val *= 100_000
                turnover_inr = val
                turnover_clause = turnover_match.group(0).strip()
            except Exception:
                pass

        # 2. Experience heuristic (e.g., 4 years of experience)
        exp_years = None
        exp_clause = None
        exp_match = re.search(r'(\d+)\s*(?:years?|yrs?)\s*(?:of\s+)?experience', text_lower)
        if exp_match:
            try:
                exp_years = int(exp_match.group(1))
                exp_clause = exp_match.group(0).strip()
            except Exception:
                pass

        # 3. Previous projects (e.g. completed 2 similar works)
        proj_count = None
        proj_clause = None
        proj_match = re.search(r'completed\s*(?:at\s+least\s*)?(\d+)\s*(?:similar)?\s*(?:projects?|works?)', text_lower)
        if proj_match:
            try:
                proj_count = int(proj_match.group(1))
                proj_clause = proj_match.group(0).strip()
            except Exception:
                pass

        # 4. GST & EMD
        gst_req = "gst" in text_lower or "gstin" in text_lower
        gst_clause = "Mandatory GST registration certificate required." if gst_req else None

        emd_amount = None
        emd_clause = None
        emd_match = re.search(r'(?:emd|earnest\s+money\s+deposit)\s*(?:of|is|:)?\s*(?:rs\.?|inr|₹)?\s*([\d,.]+)\s*(crore|cr|lakh|lakhs)?', text_lower)
        if not emd_match:
            emd_match = re.search(r'(?:emd|earnest\s+money)[^\n]{1,40}?(?:rs\.?|inr|₹)?\s*([\d,.]+)\s*(crore|cr|lakh|lakhs)?', text_lower)

        if emd_match:
            try:
                val_str = emd_match.group(1).replace(",", "")
                val = float(val_str)
                unit = (emd_match.group(2) or "").lower()
                if "cr" in unit:
                    val *= 10_000_000
                elif "lakh" in unit:
                    val *= 100_000
                emd_amount = val
                emd_clause = emd_match.group(0).strip()
            except Exception:
                pass

        # Common documents detected
        docs = []
        if gst_req:
            docs.append("GST Registration Certificate")
        if "pan" in text_lower:
            docs.append("Permanent Account Number (PAN) Card")
        if "udyam" in text_lower or "msme" in text_lower:
            docs.append("Udyam MSME Registration Certificate")
        if turnover_inr:
            docs.append("Audited Balance Sheets (Last 3 Financial Years)")
        if exp_years:
            docs.append("Client Work Completion / Experience Certificates")

        return ExtractedTenderRequirements(
            minimum_turnover_inr=turnover_inr,
            minimum_experience_years=exp_years,
            minimum_similar_projects=proj_count,
            gst_required=gst_req,
            emd_amount_inr=emd_amount,
            required_documents=docs,
            turnover_clause=turnover_clause,
            experience_clause=exp_clause,
            similar_projects_clause=proj_clause,
            gst_clause=gst_clause,
            emd_clause=emd_clause,
        )

    def extract(self, tender_text: str) -> tuple[ExtractedTenderRequirements, str]:
        """
        Attempts Gemini 2.5 Flash extraction first.
        If Gemini is not configured or encounters an error, applies heuristic extractor
        and notes the method used.
        """
        if self.is_configured():
            extracted = self.extract_with_gemini(tender_text)
            if extracted:
                return extracted, "Gemini 2.5 Flash (Structured AI Extraction)"

        extracted = self.fallback_regex_extractor(tender_text)
        method = "Heuristic Text Extractor (Add GEMINI_API_KEY in Settings to enable Gemini 2.5 Flash)"
        return extracted, method
