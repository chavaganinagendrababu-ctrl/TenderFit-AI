"""
TenderFit - Production Eligibility Matching Engine
Compares company profile & uploaded proof documents against tender requirements.
Assigns status: MET, MISSING, NEEDS VERIFICATION, NOT APPLICABLE with explicit explanations.
"""

from typing import Dict, Any, List, Optional
from eligibility.rules import EligibilityStatus


class EligibilityMatchingEngine:
    """
    Deterministic evaluation engine that cross-references company statutory records,
    financial track record, and uploaded document proofs against tender specifications.
    """

    DISCLAIMER = (
        "Notice: The Match Score and Status are algorithmic indicators for decision support only. "
        "They do not constitute official legal pre-qualification or government tender approval."
    )

    @classmethod
    def evaluate(
        cls,
        company: Dict[str, Any],
        tender_reqs: Dict[str, Any],
        company_docs: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """
        Executes full criteria matching.
        """
        company_docs = company_docs or []
        uploaded_doc_types = [
            (d.get("document_type") or "").upper()
            for d in company_docs
        ]

        criteria: List[Dict[str, Any]] = []
        missing_documents: List[str] = []
        verification_warnings: List[str] = []

        # 1. ANNUAL TURNOVER EVALUATION
        req_turnover = tender_reqs.get("minimum_turnover_inr")
        comp_turnover = float(company.get("annual_turnover") or 0.0)
        t_clause = tender_reqs.get("turnover_clause") or "Tender stipulates minimum average annual turnover."

        if req_turnover is not None and req_turnover > 0:
            if comp_turnover >= req_turnover:
                # Check if financial proof doc was uploaded
                has_audit_doc = any("TURNOVER" in dt or "AUDIT" in dt or "FINANCIAL" in dt for dt in uploaded_doc_types)
                status = EligibilityStatus.MET.value if has_audit_doc else EligibilityStatus.NEEDS_VERIFICATION.value
                reason = (
                    f"Company turnover (₹{comp_turnover:,.0f}) meets or exceeds requirement of ₹{req_turnover:,.0f}."
                    + (" Supporting audited statements attached." if has_audit_doc else " (Warning: Upload audited balance sheet to substantiate turnover).")
                )
                if not has_audit_doc:
                    verification_warnings.append("Audited balance sheet proof is recommended to confirm turnover claim.")
            else:
                status = EligibilityStatus.MISSING.value
                deficit = req_turnover - comp_turnover
                reason = f"Company turnover (₹{comp_turnover:,.0f}) falls short by ₹{deficit:,.0f} of required ₹{req_turnover:,.0f}."
            
            criteria.append({
                "criterion": "Minimum Annual Turnover",
                "status": status,
                "required": f"₹{req_turnover:,.0f}",
                "company_data": f"₹{comp_turnover:,.0f}",
                "reason": reason,
                "clause_reference": t_clause,
            })
        else:
            criteria.append({
                "criterion": "Minimum Annual Turnover",
                "status": EligibilityStatus.NOT_APPLICABLE.value,
                "required": "No minimum specified",
                "company_data": f"₹{comp_turnover:,.0f}",
                "reason": "Tender document specifies no restrictive turnover threshold.",
                "clause_reference": "N/A",
            })

        # 2. OPERATIONAL EXPERIENCE
        req_exp = tender_reqs.get("minimum_experience_years")
        comp_exp = int(company.get("years_of_experience") or 0)
        exp_clause = tender_reqs.get("experience_clause") or "Tender requires operational track record."

        if req_exp is not None and req_exp > 0:
            if comp_exp >= req_exp:
                has_exp_doc = any("EXPERIENCE" in dt for dt in uploaded_doc_types)
                status = EligibilityStatus.MET.value if has_exp_doc else EligibilityStatus.NEEDS_VERIFICATION.value
                reason = (
                    f"Company has {comp_exp} years in business (meets required {req_exp} years)."
                    + (" Experience certificate attached." if has_exp_doc else " (Recommendation: Upload client experience certificate).")
                )
                if not has_exp_doc:
                    verification_warnings.append("Upload client experience certificates to authenticate operational years.")
            else:
                status = EligibilityStatus.MISSING.value
                reason = f"Company has {comp_exp} years of operational history; tender requires at least {req_exp} years."
            
            criteria.append({
                "criterion": "Years of Experience",
                "status": status,
                "required": f"{req_exp} Years",
                "company_data": f"{comp_exp} Years",
                "reason": reason,
                "clause_reference": exp_clause,
            })
        else:
            criteria.append({
                "criterion": "Years of Experience",
                "status": EligibilityStatus.NOT_APPLICABLE.value,
                "required": "Not specified",
                "company_data": f"{comp_exp} Years",
                "reason": "No minimum operational years condition specified in tender.",
                "clause_reference": "N/A",
            })

        # 3. PREVIOUS SIMILAR PROJECTS
        req_proj = tender_reqs.get("minimum_similar_projects")
        comp_proj = int(company.get("previous_projects_count") or 0)
        proj_clause = tender_reqs.get("similar_projects_clause") or "Proof of completed similar works."

        if req_proj is not None and req_proj > 0:
            if comp_proj >= req_proj:
                has_proj_doc = any("PROJECT" in dt or "COMPLETION" in dt for dt in uploaded_doc_types)
                status = EligibilityStatus.MET.value if has_proj_doc else EligibilityStatus.NEEDS_VERIFICATION.value
                reason = f"Company has completed {comp_proj} projects (requires {req_proj})."
            else:
                status = EligibilityStatus.MISSING.value
                reason = f"Company has {comp_proj} completed projects; tender requires at least {req_proj} similar projects."

            criteria.append({
                "criterion": "Previous Similar Works",
                "status": status,
                "required": f"{req_proj} Works",
                "company_data": f"{comp_proj} Works",
                "reason": reason,
                "clause_reference": proj_clause,
            })
        else:
            criteria.append({
                "criterion": "Previous Similar Works",
                "status": EligibilityStatus.NOT_APPLICABLE.value,
                "required": "Not specified",
                "company_data": f"{comp_proj} Projects",
                "reason": "No restrictive project count threshold mandated.",
                "clause_reference": "N/A",
            })

        # 4. STATUTORY GST COMPLIANCE
        gst_req = tender_reqs.get("gst_required", True)
        comp_gst = company.get("gst_registered", False)
        comp_gstin = company.get("gst_number")
        gst_clause = tender_reqs.get("gst_clause") or "Mandatory GST registration requirement."

        if gst_req:
            has_gst_doc = any("GST" in dt for dt in uploaded_doc_types)
            if comp_gst and comp_gstin:
                status = EligibilityStatus.MET.value if has_gst_doc else EligibilityStatus.NEEDS_VERIFICATION.value
                reason = (
                    f"GST registered with GSTIN {comp_gstin}."
                    + (" GST Certificate uploaded." if has_gst_doc else " (Please upload GST certificate copy).")
                )
                if not has_gst_doc:
                    missing_documents.append("GST Registration Certificate (Copy)")
            else:
                status = EligibilityStatus.MISSING.value
                reason = "Company lacks active GST registration required by this tender."
                missing_documents.append("GST Registration Certificate")

            criteria.append({
                "criterion": "GSTIN Registration",
                "status": status,
                "required": "Mandatory Active GSTIN",
                "company_data": f"Registered ({comp_gstin})" if (comp_gst and comp_gstin) else "Not Registered",
                "reason": reason,
                "clause_reference": gst_clause,
            })

        # 5. EMD & MSME BENEFIT
        emd_amount = tender_reqs.get("emd_amount_inr")
        is_udyam = company.get("udyam_registered", False)
        udyam_no = company.get("udyam_number")
        emd_clause = tender_reqs.get("emd_clause") or "Earnest Money Deposit (EMD) terms."

        if emd_amount is not None and emd_amount > 0:
            if is_udyam:
                status = EligibilityStatus.MET.value
                reason = (
                    f"Tender EMD is ₹{emd_amount:,.0f}. However, company holds active MSME/Udyam status ({udyam_no}), "
                    "qualifying for statutory EMD exemption under public procurement policy."
                )
            else:
                status = EligibilityStatus.NEEDS_VERIFICATION.value
                reason = f"EMD amount of ₹{emd_amount:,.0f} required via Bank Guarantee/DD. Company is not registered as MSME."
                verification_warnings.append(f"Ensure EMD of ₹{emd_amount:,.0f} is budgeted and arranged.")

            criteria.append({
                "criterion": "EMD Compliance & MSME Exemption",
                "status": status,
                "required": f"₹{emd_amount:,.0f} (Exempt for MSME)",
                "company_data": f"MSME Registered ({udyam_no})" if is_udyam else "Standard Bidder (Non-MSME)",
                "reason": reason,
                "clause_reference": emd_clause,
            })

        # Calculate Overall Status & Indicative Score
        applicable_criteria = [c for c in criteria if c["status"] != EligibilityStatus.NOT_APPLICABLE.value]
        met_count = sum(1 for c in applicable_criteria if c["status"] == EligibilityStatus.MET.value)
        verify_count = sum(1 for c in applicable_criteria if c["status"] == EligibilityStatus.NEEDS_VERIFICATION.value)
        missing_count = sum(1 for c in applicable_criteria if c["status"] == EligibilityStatus.MISSING.value)

        total_app = len(applicable_criteria)
        if total_app > 0:
            # Weighted score: MET = 1.0, NEEDS_VERIFICATION = 0.5, MISSING = 0.0
            score = round(((met_count * 1.0 + verify_count * 0.5) / total_app) * 100.0, 1)
        else:
            score = 100.0

        if missing_count > 0:
            overall_status = EligibilityStatus.MISSING.value
        elif verify_count > 0:
            overall_status = EligibilityStatus.NEEDS_VERIFICATION.value
        else:
            overall_status = EligibilityStatus.MET.value

        return {
            "overall_status": overall_status,
            "match_score": score,
            "criteria": criteria,
            "missing_documents": missing_documents,
            "verification_warnings": verification_warnings,
            "disclaimer": cls.DISCLAIMER,
        }
