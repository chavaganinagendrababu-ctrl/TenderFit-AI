"""
TenderFit - Portal Scraper Base Class
Defines the contract for portal-specific scrapers and enforces security gate compliance.
"""

from abc import ABC, abstractmethod
import logging
from typing import List, Dict, Any, Optional
from playwright.sync_api import Page

logger = logging.getLogger("tenderfit.automation.portal")


class SecurityGateInterventionRequired(Exception):
    """
    Raised when a public tender portal presents a login screen, OTP request,
    CAPTCHA challenge, or Cloudflare verification that requires manual user intervention.
    In accordance with ethical automation principles, we never bypass security gates.
    """
    def __init__(self, gate_type: str, portal_url: str, message: str):
        self.gate_type = gate_type
        self.portal_url = portal_url
        self.message = message
        super().__init__(f"[{gate_type.upper()}] Manual Intervention Required at {portal_url}: {message}")


class BasePortalScraper(ABC):
    """
    Abstract Base Class for public government tender portal scrapers.
    Each specific portal (e.g., Central Public Procurement Portal, GeM, State Portals)
    subclasses this and implements portal-specific navigation and extraction.
    """

    def __init__(self, portal_name: str, base_url: str):
        self.portal_name = portal_name
        self.base_url = base_url

    def check_security_gates(self, page: Page):
        """
        Scans the current page DOM for authentication gates, OTP requests, or CAPTCHAs.
        If detected, aborts automation immediately to protect portal terms and security.
        """
        html_lower = page.content().lower()

        # 1. CAPTCHA detection
        captcha_indicators = [
            "g-recaptcha",
            "hcaptcha",
            "cf-turnstile",
            "enter the captcha",
            "captcha image",
            "enter security code",
            "verify you are human",
        ]
        for indicator in captcha_indicators:
            if indicator in html_lower:
                logger.warning(f"Security gate encountered on {self.portal_name}: CAPTCHA challenge detected.")
                raise SecurityGateInterventionRequired(
                    gate_type="CAPTCHA_DETECTED",
                    portal_url=page.url,
                    message="A CAPTCHA challenge was encountered. Please complete verification manually."
                )

        # 2. Login / Authentication gate detection
        login_indicators = [
            "please login to view tender",
            "enter your password",
            "enter otp sent to",
            "enter two-factor code",
            "authorization required",
        ]
        for indicator in login_indicators:
            if indicator in html_lower:
                logger.warning(f"Security gate encountered on {self.portal_name}: Login/OTP required.")
                raise SecurityGateInterventionRequired(
                    gate_type="AUTHENTICATION_REQUIRED",
                    portal_url=page.url,
                    message="Portal requires user credentials or an OTP. Manual intervention required."
                )

    @abstractmethod
    def navigate_to_listing(self, page: Page):
        """Navigate to the main tender search or listing page."""
        pass

    @abstractmethod
    def search_tenders(self, page: Page, category: str, keywords: Optional[str] = None) -> List[Dict[str, Any]]:
        """Perform search by category and return a list of extracted tender summary dictionaries."""
        pass

    @abstractmethod
    def extract_tender_details(self, page: Page, tender_url: str) -> Dict[str, Any]:
        """Navigate to individual tender detail page and extract full metadata."""
        pass

