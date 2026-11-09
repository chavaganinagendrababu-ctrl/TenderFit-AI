"""
TenderFit - Download Manager
Safely downloads, verifies, and organizes tender PDF documents into directories.
"""

import os
import re
import logging
from pathlib import Path
from typing import Optional
from playwright.sync_api import Page, Download

from config.settings import settings

logger = logging.getLogger("tenderfit.automation.download")


class DownloadManager:
    """
    Manages downloading tender notices, specification sheets, and corrigendum PDFs.
    Organizes files under documents/tender_documents/<sanitized_tender_id>/.
    """

    def __init__(self, base_dir: Optional[Path] = None):
        self.base_dir = base_dir or settings.TENDER_DOCS_DIR
        self.base_dir.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def sanitize_filename(name: str) -> str:
        """Removes illegal filesystem characters from filenames."""
        sanitized = re.sub(r'[<>:"/\\|?*]', "_", name)
        return sanitized[:150]

    def get_tender_folder(self, tender_id: str) -> Path:
        """Returns and creates the dedicated storage path for a tender's attachments."""
        safe_id = self.sanitize_filename(tender_id)
        folder = self.base_dir / safe_id
        folder.mkdir(parents=True, exist_ok=True)
        return folder

    def save_download(self, download: Download, tender_id: str, suggested_name: Optional[str] = None) -> Path:
        """
        Saves a Playwright Download object into the target directory.
        Returns the absolute Path of the saved file.
        """
        folder = self.get_tender_folder(tender_id)
        filename = suggested_name or download.suggested_filename or "tender_document.pdf"
        filename = self.sanitize_filename(filename)

        if not filename.lower().endswith(".pdf"):
            filename += ".pdf"

        target_path = folder / filename
        logger.info(f"Saving tender attachment for '{tender_id}' to {target_path}...")
        download.save_as(str(target_path))

        # Verification: check file exists and is not 0 bytes
        if target_path.exists() and target_path.stat().st_size > 0:
            logger.info(f"Downloaded successfully: {filename} ({target_path.stat().st_size} bytes)")
            return target_path
        else:
            raise IOError(f"Downloaded file {target_path} is empty or missing.")

    def save_stream_bytes(self, content: bytes, tender_id: str, filename: str) -> Path:
        """Saves raw PDF bytes when downloaded via direct HTTP response."""
        folder = self.get_tender_folder(tender_id)
        safe_name = self.sanitize_filename(filename)
        if not safe_name.lower().endswith(".pdf"):
            safe_name += ".pdf"

        target_path = folder / safe_name
        with open(target_path, "wb") as f:
            f.write(content)
        return target_path

