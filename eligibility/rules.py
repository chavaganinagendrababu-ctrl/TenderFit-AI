"""
TenderFit - Eligibility Evaluation Rules & Status Enums
"""

from enum import Enum


class EligibilityStatus(str, Enum):
    MET = "MET"
    MISSING = "MISSING"
    NEEDS_VERIFICATION = "NEEDS VERIFICATION"
    NOT_APPLICABLE = "NOT APPLICABLE"

