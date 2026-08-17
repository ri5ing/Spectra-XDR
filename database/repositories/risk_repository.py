"""Async Repository for Risk Assessment Persistence."""

import uuid
from typing import Optional, Dict, Any
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.risk import RiskAssessment


class RiskRepository:
    """Repository handling persistence of Risk Assessments."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def save_risk_assessment(self, incident_id: uuid.UUID, risk_score: float, risk_level: str, breakdown: Dict[str, Any]) -> RiskAssessment:
        """Create and persist a risk assessment."""
        assessment = RiskAssessment(
            incident_id=incident_id,
            risk_score=risk_score,
            risk_level=risk_level,
            score_breakdown=breakdown
        )
        self.session.add(assessment)
        await self.session.commit()
        await self.session.refresh(assessment)
        return assessment

    async def get_latest_risk_assessment(self, incident_id: uuid.UUID) -> Optional[RiskAssessment]:
        """Get latest risk assessment for an incident."""
        stmt = (
            select(RiskAssessment)
            .where(RiskAssessment.incident_id == incident_id)
            .order_by(RiskAssessment.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()
