"""Phase 4 Detection and correlation schema migration

Revision ID: 003_detection
Revises: 002_intelligence
Create Date: 2026-08-17 21:45:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '003_detection'
down_revision: Union[str, None] = '002_intelligence'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create detection_rules table
    op.create_table(
        'detection_rules',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('rule_id', sa.String(length=50), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('version', sa.String(length=50), server_default='1.0.0', nullable=False),
        sa.Column('enabled', sa.Boolean(), server_default='true', nullable=False),
        sa.Column('severity', sa.String(length=50), server_default='medium', nullable=False),
        sa.Column('condition_type', sa.String(length=50), nullable=False),
        sa.Column('condition_config', sa.JSON(), nullable=False),
        sa.Column('mitre_technique_id', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_detection_rules_rule_id'), 'detection_rules', ['rule_id'], unique=True)
    op.create_index(op.f('ix_detection_rules_enabled'), 'detection_rules', ['enabled'], unique=False)

    # 2. Create detection_matches table
    op.create_table(
        'detection_matches',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('detection_rule_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('incident_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('matched_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('window_start', sa.DateTime(timezone=True), nullable=True),
        sa.Column('window_end', sa.DateTime(timezone=True), nullable=True),
        sa.Column('event_count', sa.Integer(), server_default='1', nullable=False),
        sa.Column('match_reason', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['detection_rule_id'], ['detection_rules.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['incident_id'], ['incidents.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('detection_rule_id', 'incident_id', 'window_start', 'window_end', name='uq_detection_match_window')
    )
    op.create_index(op.f('ix_detection_matches_detection_rule_id'), 'detection_matches', ['detection_rule_id'], unique=False)
    op.create_index(op.f('ix_detection_matches_incident_id'), 'detection_matches', ['incident_id'], unique=False)
    op.create_index(op.f('ix_detection_matches_matched_at'), 'detection_matches', ['matched_at'], unique=False)

    # 3. Create incident_evidence table
    op.create_table(
        'incident_evidence',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('incident_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('event_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('detection_match_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('evidence_type', sa.String(length=50), nullable=False),
        sa.Column('evidence_data', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['detection_match_id'], ['detection_matches.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['event_id'], ['events.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['incident_id'], ['incidents.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('incident_id', 'event_id', 'detection_match_id', 'evidence_type', name='uq_incident_evidence_record')
    )
    op.create_index(op.f('ix_incident_evidence_incident_id'), 'incident_evidence', ['incident_id'], unique=False)
    op.create_index(op.f('ix_incident_evidence_event_id'), 'incident_evidence', ['event_id'], unique=False)
    op.create_index(op.f('ix_incident_evidence_detection_match_id'), 'incident_evidence', ['detection_match_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_incident_evidence_detection_match_id'), table_name='incident_evidence')
    op.drop_index(op.f('ix_incident_evidence_event_id'), table_name='incident_evidence')
    op.drop_index(op.f('ix_incident_evidence_incident_id'), table_name='incident_evidence')
    op.drop_table('incident_evidence')

    op.drop_index(op.f('ix_detection_matches_matched_at'), table_name='detection_matches')
    op.drop_index(op.f('ix_detection_matches_incident_id'), table_name='detection_matches')
    op.drop_index(op.f('ix_detection_matches_detection_rule_id'), table_name='detection_matches')
    op.drop_table('detection_matches')

    op.drop_index(op.f('ix_detection_rules_enabled'), table_name='detection_rules')
    op.drop_index(op.f('ix_detection_rules_rule_id'), table_name='detection_rules')
    op.drop_table('detection_rules')
