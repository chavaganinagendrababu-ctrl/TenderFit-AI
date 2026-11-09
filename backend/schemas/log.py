"""
TenderFit - Pydantic Schemas for Automation Logs
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class AutomationLogCreate(BaseModel):
    portal_name: str
    action: str
    status: str
    message: str
    details_json: Optional[str] = None


class AutomationLogResponse(AutomationLogCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    timestamp: datetime

