"""Phase 5 Incident investigation and analyst workflow schema migration

Revision ID: 004_investigation
Revises: 003_detection
Create Date: 2026-08-17 22:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '004_investigation'
down_revision: Union[str, None] = '003_detection'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Add workflow columns to incidents
    op.add_column('incidents', sa.Column('assigned_to', sa.String(length=255), nullable=True))
    op.add_column('incidents', sa.Column('resolution', sa.Text(), nullable=True))
    op.add_column('incidents', sa.Column('resolved_at', sa.DateTime(timezone=True), nullable=True))
    op.create_index(op.f('ix_incidents_assigned_to'), 'incidents', ['assigned_to'], unique=False)

    # 2. Create incident_notes table
    op.create_table(
        'incident_notes',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('incident_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('author', sa.String(length=255), server_default='analyst', nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['incident_id'], ['incidents.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_incident_notes_incident_id'), 'incident_notes', ['incident_id'], unique=False)

    # 3. Create incident_audit_log table
    op.create_table(
        'incident_audit_log',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('incident_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('action', sa.String(length=100), nullable=False),
        sa.Column('field_name', sa.String(length=100), nullable=True),
        sa.Column('old_value', sa.String(length=255), nullable=True),
        sa.Column('new_value', sa.String(length=255), nullable=True),
        sa.Column('actor', sa.String(length=255), server_default='analyst', nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('metadata', sa.JSON(), nullable=False),
        sa.ForeignKeyConstraint(['incident_id'], ['incidents.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_incident_audit_log_incident_id'), 'incident_audit_log', ['incident_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_incident_audit_log_incident_id'), table_name='incident_audit_log')
    op.drop_table('incident_audit_log')

    op.drop_index(op.f('ix_incident_notes_incident_id'), table_name='incident_notes')
    op.drop_table('incident_notes')

    op.drop_index(op.f('ix_incidents_assigned_to'), table_name='incidents')
    op.drop_column('incidents', 'resolved_at')
    op.drop_column('incidents', 'resolution')
    op.drop_column('incidents', 'assigned_to')
