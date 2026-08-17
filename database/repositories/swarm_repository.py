"""Async Repository for Swarm Execution Records."""

import uuid
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from database.models.swarm import SwarmRun, AgentThoughtRecord
from agents.models import SwarmState


class SwarmRepository:
    """Repository handling persistence of AI Swarm runs and agent thoughts."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def save_swarm_run(self, state: SwarmState) -> SwarmRun:
        """Persist a SwarmState object as a SwarmRun record with AgentThoughts."""
        swarm_run = SwarmRun(
            incident_id=state.incident_id,
            human_incident_id=state.incident_human_id,
            current_agent=state.current_agent.value if hasattr(state.current_agent, "value") else str(state.current_agent),
            completed_agents=[a.value if hasattr(a, "value") else str(a) for a in state.completed_agents],
            attack_chain=state.attack_chain,
            risk_score=state.risk_score,
            risk_level=state.risk_level,
            human_approval_required=state.human_approval_required,
            human_approval_status=state.human_approval_status.value if hasattr(state.human_approval_status, "value") else str(state.human_approval_status)
        )
        self.session.add(swarm_run)
        await self.session.flush()

        for thought in state.thoughts:
            thought_rec = AgentThoughtRecord(
                swarm_run_id=swarm_run.id,
                agent_role=thought.agent_role.value if hasattr(thought.agent_role, "value") else str(thought.agent_role),
                model_used=thought.model_used.value if hasattr(thought.model_used, "value") else str(thought.model_used),
                summary=thought.summary,
                findings=thought.findings,
                confidence=thought.confidence,
                created_at=thought.timestamp
            )
            self.session.add(thought_rec)

        await self.session.commit()
        await self.session.refresh(swarm_run)
        return swarm_run

    async def get_latest_swarm_run(self, incident_id: uuid.UUID) -> Optional[SwarmRun]:
        """Fetch latest swarm run for an incident with thoughts loaded."""
        stmt = (
            select(SwarmRun)
            .where(SwarmRun.incident_id == incident_id)
            .options(selectinload(SwarmRun.thoughts))
            .order_by(SwarmRun.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()
