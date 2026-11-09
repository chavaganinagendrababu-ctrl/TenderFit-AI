"""
TenderFit - PDF Text and Clause Extraction Module (PyMuPDF)
Extracts raw text, table content, and eligibility condition clauses from tender documents.
"""

import logging
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger("tenderfit.pdf_processing")


class TenderPDFExtractor:
    """
    Extracts text and tabular content from tender PDFs using PyMuPDF (fitz).
    Gracefully flags scanned documents requiring OCR or manual review.
    """

    def __init__(self, pdf_path: str | Path):
        self.pdf_path = Path(pdf_path)

    def extract_text(self) -> Dict[str, Any]:
        """
        Extracts full text and page-by-page content.
        Flags whether PDF contains digital text or appears to be a scanned image.
        """
        if not self.pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {self.pdf_path}")

        try:
            import fitz  # PyMuPDF
        except ImportError:
            raise ImportError("PyMuPDF is not installed. Run 'pip install PyMuPDF'.")

        doc = fitz.open(str(self.pdf_path))
        total_pages = len(doc)
        full_text = []
        is_scanned = True

        for page_num in range(total_pages):
            page = doc[page_num]
            text = page.get_text("text")
            if text and len(text.strip()) > 30:
                is_scanned = False
            full_text.append({"page": page_num + 1, "text": text})

        doc.close()

        combined_text = "\n\n".join([p["text"] for p in full_text])
        return {
            "total_pages": total_pages,
            "is_scanned": is_scanned,
            "pages": full_text,
            "full_text": combined_text,
            "needs_ocr_review": is_scanned,
        }

