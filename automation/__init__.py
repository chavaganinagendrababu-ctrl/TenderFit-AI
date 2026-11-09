"""Automation package for TenderFit."""
from automation.browser_manager import BrowserManager
from automation.download_manager import DownloadManager
from automation.portal_base import BasePortalScraper, SecurityGateInterventionRequired
from automation.tender_scraper import (
    TenderScraperCoordinator,
    PublicGovernmentPortalScraper,
    PublicGovernmentPortalScraper as CPPPPublicPortalScraper,
)

__all__ = [
    "BrowserManager",
    "DownloadManager",
    "BasePortalScraper",
    "SecurityGateInterventionRequired",
    "TenderScraperCoordinator",
    "PublicGovernmentPortalScraper",
    "CPPPPublicPortalScraper",
]

