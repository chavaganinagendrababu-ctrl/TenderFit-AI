"""
TenderFit - Automation Logs API Routes
Endpoints to monitor scraping runs, security checks, and audit trails.
"""

from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.schemas.log import AutomationLogCreate, AutomationLogResponse
from backend.services.tender_service import LogService

router = APIRouter(prefix="/api/logs", tags=["Automation Logs"])


@router.get("/", response_model=List[AutomationLogResponse])
def get_logs(limit: int = 50, db: Session = Depends(get_db)):
    """Retrieve recent automation and scraping logs."""
    return LogService.list_logs(db, limit=limit)


@router.post("/", response_model=AutomationLogResponse, status_code=status.HTTP_201_CREATED)
def create_log(log_in: AutomationLogCreate, db: Session = Depends(get_db)):
    """Record an automation log entry."""
    return LogService.log_action(
        db=db,
        portal_name=log_in.portal_name,
        action=log_in.action,
        status_val=log_in.status,
        message=log_in.message,
        details_json=log_in.details_json,
    )

