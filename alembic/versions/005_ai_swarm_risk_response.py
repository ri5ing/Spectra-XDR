"""005_ai_swarm_risk_response migration.

Revision ID: 005_ai_swarm_risk_response
Revises: 004_incident_investigation
Create Date: 2026-08-17 23:30:00.000000
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '005_ai_swarm_risk_response'
down_revision: Union[str, None] = '004_incident_investigation'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Swarm Runs Table
    op.create_table(
        'swarm_runs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('incident_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('incidents.id', ondelete='CASCADE'), nullable=False),
        sa.Column('human_incident_id', sa.String(64), nullable=False),
        sa.Column('current_agent', sa.String(64), nullable=False, server_default='supervisor'),
        sa.Column('completed_agents', sa.JSON(), nullable=False),
        sa.Column('attack_chain', sa.JSON(), nullable=False),
        sa.Column('risk_score', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('risk_level', sa.String(32), nullable=False, server_default='LOW'),
        sa.Column('human_approval_required', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('human_approval_status', sa.String(32), nullable=False, server_default='not_required'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()'))
    )
    op.create_index('ix_swarm_runs_incident_id', 'swarm_runs', ['incident_id'])

    # 2. Agent Thought Records Table
    op.create_table(
        'agent_thought_records',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('swarm_run_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('swarm_runs.id', ondelete='CASCADE'), nullable=False),
        sa.Column('agent_role', sa.String(64), nullable=False),
        sa.Column('model_used', sa.String(64), nullable=False),
        sa.Column('summary', sa.Text(), nullable=False),
        sa.Column('findings', sa.JSON(), nullable=False),
        sa.Column('confidence', sa.Float(), nullable=False, server_default='0.9'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()'))
    )
    op.create_index('ix_agent_thought_records_swarm_run_id', 'agent_thought_records', ['swarm_run_id'])

    # 3. Risk Assessments Table
    op.create_table(
        'risk_assessments',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('incident_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('incidents.id', ondelete='CASCADE'), nullable=False),
        sa.Column('risk_score', sa.Float(), nullable=False),
        sa.Column('risk_level', sa.String(32), nullable=False),
        sa.Column('score_breakdown', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()'))
    )
    op.create_index('ix_risk_assessments_incident_id', 'risk_assessments', ['incident_id'])

    # 4. Response Actions Table
    op.create_table(
        'response_actions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('incident_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('incidents.id', ondelete='CASCADE'), nullable=False),
        sa.Column('action_type', sa.String(64), nullable=False),
        sa.Column('target', sa.String(256), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('high_impact', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('approval_status', sa.String(32), nullable=False, server_default='pending_approval'),
        sa.Column('approved_by', sa.String(128), nullable=True),
        sa.Column('execution_status', sa.String(32), nullable=False, server_default='PENDING'),
        sa.Column('execution_result', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('executed_at', sa.DateTime(timezone=True), nullable=True)
    )
    op.create_index('ix_response_actions_incident_id', 'response_actions', ['incident_id'])

    # 5. Audit Trail Table
    op.create_table(
        'audit_trail',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('incident_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('actor', sa.String(128), nullable=False),
        sa.Column('action', sa.String(128), nullable=False),
        sa.Column('details', sa.JSON(), nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()'))
    )
    op.create_index('ix_audit_trail_incident_id', 'audit_trail', ['incident_id'])


def downgrade() -> None:
    op.drop_table('audit_trail')
    op.drop_table('response_actions')
    op.drop_table('risk_assessments')
    op.drop_table('agent_thought_records')
    op.drop_table('swarm_runs')
