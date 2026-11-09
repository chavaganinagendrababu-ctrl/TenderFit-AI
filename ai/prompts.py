"""
TenderFit - Gemini Prompt Engineering Templates
Structured prompts designed to extract tender requirements with exact clause traceability.
"""

TENDER_REQUIREMENT_EXTRACTION_SYSTEM_PROMPT = """You are an expert Government Procurement and Legal Tender Analyst.
Your task is to analyze tender document text and extract verifiable eligibility criteria into strict JSON.

CRITICAL RULES:
1. NEVER invent or assume requirements. If a condition is not mentioned in the text, set its value to null.
2. For EVERY condition you extract, you MUST provide the EXACT sentence or clause from the tender text as "evidence_clause".
3. Return ONLY valid JSON adhering to the specified schema. No markdown formatting, no commentary.
"""

TENDER_REQUIREMENT_EXTRACTION_USER_PROMPT = """Extract the eligibility criteria from the following government tender text:

--- TENDER TEXT START ---
{tender_text}
--- TENDER TEXT END ---

Return a JSON object with this exact structure:
{{
  "minimum_turnover_inr": <number or null>,
  "minimum_experience_years": <number or null>,
  "minimum_similar_projects": <number or null>,
  "gst_required": <boolean or null>,
  "emd_amount_inr": <number or null>,
  "required_certificates": [<string>, ...],
  "technical_qualifications": [<string>, ...],
  "evidence_clauses": {{
    "turnover_clause": "<verbatim clause from text or null>",
    "experience_clause": "<verbatim clause from text or null>",
    "projects_clause": "<verbatim clause from text or null>",
    "gst_clause": "<verbatim clause from text or null>",
    "emd_clause": "<verbatim clause from text or null>"
  }}
}}
"""

