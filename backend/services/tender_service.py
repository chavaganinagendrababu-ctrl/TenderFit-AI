"""
TenderFit - Tender and Log Service
Handles tender registration, retrieval, and automation logging.
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from backend.models.tender import Tender, TenderRequirement, EligibilityResult
from backend.models.log import AutomationLog
from backend.schemas.tender import TenderCreate
from backend.schemas.log import AutomationLogCreate


class TenderService:
    @staticmethod
    def get_by_tender_id(db: Session, tender_id: str) -> Optional[Tender]:
        """Fetch a tender by its unique portal tender ID."""
        return db.query(Tender).filter(Tender.tender_id == tender_id).first()

    @staticmethod
    def get_by_id(db: Session, id: int) -> Optional[Tender]:
        return db.query(Tender).filter(Tender.id == id).first()

    @staticmethod
    def list_tenders(
        db: Session,
        category: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Tender]:
        query = db.query(Tender)
        if category:
            query = query.filter(Tender.category.ilike(f"%{category}%"))
        return query.order_by(Tender.created_at.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def create_or_update_tender(db: Session, data: TenderCreate) -> Tender:
        """Upsert tender from scraper results."""
        tender = TenderService.get_by_tender_id(db, data.tender_id)
        if tender:
            # Update fields
            for key, val in data.model_dump().items():
                setattr(tender, key, val)
        else:
            tender = Tender(**data.model_dump())
            db.add(tender)

        db.commit()
        db.refresh(tender)
        return tender


class LogService:
    @staticmethod
    def log_action(
        db: Session,
        portal_name: str,
        action: str,
        status_val: str,
        message: str,
        details_json: Optional[str] = None,
    ) -> AutomationLog:
        """Records an audit log entry into the database."""
        log_entry = AutomationLog(
            portal_name=portal_name,
            action=action,
            status=status_val,
            message=message,
            details_json=details_json,
        )
        db.add(log_entry)
        db.commit()
        db.refresh(log_entry)
        return log_entry

    @staticmethod
    def list_logs(db: Session, limit: int = 50) -> List[AutomationLog]:
        return db.query(AutomationLog).order_by(AutomationLog.timestamp.desc()).limit(limit).all()

