"""
Unit Tests for Automation Security Gates and Download Manager
"""

import pytest
from unittest.mock import MagicMock
from automation.portal_base import BasePortalScraper, SecurityGateInterventionRequired
from automation.download_manager import DownloadManager


class DummyScraper(BasePortalScraper):
    def __init__(self):
        super().__init__("Dummy Portal", "https://example.com")

    def navigate_to_listing(self, page):
        pass

    def search_tenders(self, page, category, keywords=None):
        return []

    def extract_tender_details(self, page, tender_url):
        return {}


def test_security_gate_triggers_on_captcha():
    scraper = DummyScraper()
    mock_page = MagicMock()
    mock_page.content.return_value = "<html><body>Please enter the captcha image text to continue</body></html>"
    mock_page.url = "https://example.com/search"

    with pytest.raises(SecurityGateInterventionRequired) as exc_info:
        scraper.check_security_gates(mock_page)

    assert "CAPTCHA" in exc_info.value.gate_type


def test_security_gate_triggers_on_login():
    scraper = DummyScraper()
    mock_page = MagicMock()
    mock_page.content.return_value = "<html><body>Please login to view tender details. Enter your password.</body></html>"
    mock_page.url = "https://example.com/details"

    with pytest.raises(SecurityGateInterventionRequired) as exc_info:
        scraper.check_security_gates(mock_page)

    assert "AUTHENTICATION" in exc_info.value.gate_type


def test_download_manager_sanitization(tmp_path):
    dm = DownloadManager(base_dir=tmp_path)
    dirty_name = 'Tender:2024/PWD/Road?*<Project>.pdf'
    clean = dm.sanitize_filename(dirty_name)
    assert ":" not in clean
    assert "/" not in clean
    assert "?" not in clean
    assert "<" not in clean

