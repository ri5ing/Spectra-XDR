"""Phase 3 Intelligence foundation schema migration

Revision ID: 002_intelligence
Revises: 001_initial
Create Date: 2026-08-17 21:30:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '002_intelligence'
down_revision: Union[str, None] = '001_initial'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create iocs table
    op.create_table(
        'iocs',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('type', sa.String(length=50), nullable=False),
        sa.Column('value', sa.String(length=2048), nullable=False),
        sa.Column('normalized_value', sa.String(length=2048), nullable=False),
        sa.Column('source', sa.String(length=50), server_default='wazuh', nullable=False),
        sa.Column('confidence', sa.Float(), server_default='1.0', nullable=False),
        sa.Column('first_seen', sa.DateTime(timezone=True), nullable=False),
        sa.Column('last_seen', sa.DateTime(timezone=True), nullable=False),
        sa.Column('evidence', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_iocs_type'), 'iocs', ['type'], unique=False)
    op.create_index(op.f('ix_iocs_normalized_value'), 'iocs', ['normalized_value'], unique=False)

    # 2. Create mitre_techniques table
    op.create_table(
        'mitre_techniques',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('technique_id', sa.String(length=50), nullable=False),
        sa.Column('technique_name', sa.String(length=255), nullable=False),
        sa.Column('tactic', sa.String(length=100), nullable=False),
        sa.Column('subtechnique_id', sa.String(length=50), nullable=True),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('detection_rationale', sa.Text(), nullable=False),
        sa.Column('source', sa.String(length=50), server_default='spectra_catalog', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_mitre_techniques_technique_id'), 'mitre_techniques', ['technique_id'], unique=True)
    op.create_index(op.f('ix_mitre_techniques_tactic'), 'mitre_techniques', ['tactic'], unique=False)

    # 3. Create event_iocs junction table
    op.create_table(
        'event_iocs',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('event_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('ioc_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['event_id'], ['events.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['ioc_id'], ['iocs.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_event_iocs_event_id'), 'event_iocs', ['event_id'], unique=False)
    op.create_index(op.f('ix_event_iocs_ioc_id'), 'event_iocs', ['ioc_id'], unique=False)

    # 4. Create event_mitre_mappings junction table
    op.create_table(
        'event_mitre_mappings',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('event_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('technique_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('matched_rule_id', sa.String(length=100), nullable=True),
        sa.Column('matched_group', sa.String(length=100), nullable=True),
        sa.Column('confidence', sa.Float(), server_default='1.0', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['event_id'], ['events.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['technique_id'], ['mitre_techniques.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_event_mitre_mappings_event_id'), 'event_mitre_mappings', ['event_id'], unique=False)
    op.create_index(op.f('ix_event_mitre_mappings_technique_id'), 'event_mitre_mappings', ['technique_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_event_mitre_mappings_technique_id'), table_name='event_mitre_mappings')
    op.drop_index(op.f('ix_event_mitre_mappings_event_id'), table_name='event_mitre_mappings')
    op.drop_table('event_mitre_mappings')

    op.drop_index(op.f('ix_event_iocs_ioc_id'), table_name='event_iocs')
    op.drop_index(op.f('ix_event_iocs_event_id'), table_name='event_iocs')
    op.drop_table('event_iocs')

    op.drop_index(op.f('ix_mitre_techniques_tactic'), table_name='mitre_techniques')
    op.drop_index(op.f('ix_mitre_techniques_technique_id'), table_name='mitre_techniques')
    op.drop_table('mitre_techniques')

    op.drop_index(op.f('ix_iocs_normalized_value'), table_name='iocs')
    op.drop_index(op.f('ix_iocs_type'), table_name='iocs')
    op.drop_table('iocs')
