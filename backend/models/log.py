"""
TenderFit - Automation Logging Model
Tracks portal scraping, downloads, manual intervention triggers, and system events.
"""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime

from backend.database import Base


def utc_now():
    return datetime.now(timezone.utc)


class AutomationLog(Base):
    """
    Audit log for web scraping runs, document downloads, CAPTCHA/login events, and engine executions.
    """
    __tablename__ = "automation_logs"

    id = Column(Integer, primary_key=True, index=True)
    portal_name = Column(String(100), nullable=False, index=True)
    action = Column(String(100), nullable=False)  # e.g., 'SEARCH', 'METADATA_EXTRACTION', 'DOWNLOAD_PDF'
    status = Column(String(50), nullable=False)   # SUCCESS, WARNING, FAILED, MANUAL_INTERVENTION_REQUIRED
    message = Column(Text, nullable=False)
    details_json = Column(Text, nullable=True)

    timestamp = Column(DateTime, default=utc_now, nullable=False, index=True)

    def __repr__(self):
        return f"<AutomationLog(id={self.id}, action='{self.action}', status='{self.status}')>"

