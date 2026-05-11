"""Extend RCA reports + add knowledge writebacks table.

Revision ID: 005
Revises: 004
"""
from alembic import op
import sqlalchemy as sa

revision = "005"
down_revision = "004"
branch_labels = None
depends_on = None


def upgrade():
    # Extend RCA reports
    with op.batch_alter_table("incident_rca_reports") as batch_op:
        batch_op.add_column(sa.Column("timeline_summary", sa.Text(), nullable=True))
        batch_op.add_column(sa.Column("impact_assessment", sa.Text(), nullable=True))
        batch_op.add_column(sa.Column("supporting_evidence_ids_json", sa.JSON(), nullable=True))
        batch_op.add_column(sa.Column("executed_action_ids_json", sa.JSON(), nullable=True))
        batch_op.add_column(sa.Column("archive_ref", sa.String(), nullable=True))
        batch_op.add_column(sa.Column("created_at", sa.DateTime(), nullable=True))

    # Knowledge writebacks table
    op.create_table(
        "incident_knowledge_writebacks",
        sa.Column("writeback_id", sa.String(), primary_key=True),
        sa.Column("run_id", sa.String(), sa.ForeignKey("incident_runs.run_id"), nullable=False),
        sa.Column("target", sa.String(), nullable=False),
        sa.Column("content_json", sa.JSON(), nullable=True),
        sa.Column("metadata_json", sa.JSON(), nullable=True),
        sa.Column("status", sa.String(), nullable=False, server_default="PENDING"),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_writebacks_run_id", "incident_knowledge_writebacks", ["run_id"])


def downgrade():
    op.drop_index("ix_writebacks_run_id", table_name="incident_knowledge_writebacks")
    op.drop_table("incident_knowledge_writebacks")
    with op.batch_alter_table("incident_rca_reports") as batch_op:
        batch_op.drop_column("created_at")
        batch_op.drop_column("archive_ref")
        batch_op.drop_column("executed_action_ids_json")
        batch_op.drop_column("supporting_evidence_ids_json")
        batch_op.drop_column("impact_assessment")
        batch_op.drop_column("timeline_summary")
