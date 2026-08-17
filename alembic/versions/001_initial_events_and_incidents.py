"""Initial events and incidents schema migration

Revision ID: 001_initial
Revises: 
Create Date: 2026-08-17 19:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '001_initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create incident_id_seq sequence
    op.execute(sa.schema.CreateSequence(sa.Sequence('incident_id_seq', start=1)))

    # 2. Create incidents table FIRST
    op.create_table(
        'incidents',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('incident_id', sa.String(length=50), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('status', sa.String(length=50), server_default='open', nullable=False),
        sa.Column('severity', sa.String(length=50), server_default='medium', nullable=False),
        sa.Column('first_seen', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_seen', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_incidents_incident_id'), 'incidents', ['incident_id'], unique=True)
    op.create_index(op.f('ix_incidents_status'), 'incidents', ['status'], unique=False)
    op.create_index(op.f('ix_incidents_severity'), 'incidents', ['severity'], unique=False)

    # 3. Create events table SECOND (referencing incidents.id)
    op.create_table(
        'events',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('event_id', sa.String(length=255), nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False),
        sa.Column('source', sa.String(length=50), server_default='wazuh', nullable=False),
        sa.Column('agent_id', sa.String(length=100), nullable=True),
        sa.Column('agent_name', sa.String(length=255), nullable=True),
        sa.Column('agent_ip', sa.String(length=50), nullable=True),
        sa.Column('rule_id', sa.String(length=100), nullable=True),
        sa.Column('rule_level', sa.Integer(), nullable=True),
        sa.Column('rule_description', sa.Text(), nullable=True),
        sa.Column('event_type', sa.String(length=100), nullable=True),
        sa.Column('location', sa.Text(), nullable=True),
        sa.Column('raw_event', sa.JSON(), nullable=False),
        sa.Column('incident_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['incident_id'], ['incidents.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_events_event_id'), 'events', ['event_id'], unique=False)
    op.create_index(op.f('ix_events_timestamp'), 'events', ['timestamp'], unique=False)
    op.create_index(op.f('ix_events_source'), 'events', ['source'], unique=False)
    op.create_index(op.f('ix_events_agent_id'), 'events', ['agent_id'], unique=False)
    op.create_index(op.f('ix_events_rule_id'), 'events', ['rule_id'], unique=False)
    op.create_index(op.f('ix_events_incident_id'), 'events', ['incident_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_events_incident_id'), table_name='events')
    op.drop_index(op.f('ix_events_rule_id'), table_name='events')
    op.drop_index(op.f('ix_events_agent_id'), table_name='events')
    op.drop_index(op.f('ix_events_source'), table_name='events')
    op.drop_index(op.f('ix_events_timestamp'), table_name='events')
    op.drop_index(op.f('ix_events_event_id'), table_name='events')
    op.drop_table('events')

    op.drop_index(op.f('ix_incidents_severity'), table_name='incidents')
    op.drop_index(op.f('ix_incidents_status'), table_name='incidents')
    op.drop_index(op.f('ix_incidents_incident_id'), table_name='incidents')
    op.drop_table('incidents')

    op.execute(sa.schema.DropSequence(sa.Sequence('incident_id_seq')))
