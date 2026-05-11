"""initial schema - existing 6 tables

Revision ID: 001
Revises: None
Create Date: 2026-03-28
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "incident_runs",
        sa.Column("run_id", sa.String(), primary_key=True),
        sa.Column("thread_id", sa.String(), nullable=False),
        sa.Column("ticket_id", sa.String(), nullable=True),
        sa.Column("status", sa.String(), nullable=False, server_default="NEW"),
        sa.Column("severity", sa.String(), nullable=True),
        sa.Column("service", sa.String(), nullable=True),
        sa.Column("env", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
        sa.Column("started_by", sa.String(), nullable=True),
    )

    op.create_table(
        "incident_checkpoints",
        sa.Column("checkpoint_id", sa.String(), primary_key=True),
        sa.Column("run_id", sa.String(), sa.ForeignKey("incident_runs.run_id"), nullable=False),
        sa.Column("node_name", sa.String(), nullable=False),
        sa.Column("state_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "incident_evidence",
        sa.Column("evidence_id", sa.String(), primary_key=True),
        sa.Column("run_id", sa.String(), sa.ForeignKey("incident_runs.run_id"), nullable=False),
        sa.Column("tool_name", sa.String(), nullable=False),
        sa.Column("category", sa.String(), nullable=False),
        sa.Column("source_ref", sa.String(), nullable=False),
        sa.Column("summary", sa.String(), nullable=False),
        sa.Column("raw_payload_json", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "incident_approvals",
        sa.Column("approval_id", sa.String(), primary_key=True),
        sa.Column("run_id", sa.String(), sa.ForeignKey("incident_runs.run_id"), nullable=False),
        sa.Column("action_json", sa.JSON(), nullable=False),
        sa.Column("risk_level", sa.String(), nullable=False),
        sa.Column("status", sa.String(), nullable=False, server_default="PENDING"),
        sa.Column("approver", sa.String(), nullable=True),
        sa.Column("comment", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "incident_actions",
        sa.Column("action_id", sa.String(), primary_key=True),
        sa.Column("run_id", sa.String(), sa.ForeignKey("incident_runs.run_id"), nullable=False),
        sa.Column("idempotency_key", sa.String(), nullable=True, unique=True),
        sa.Column("action_type", sa.String(), nullable=False),
        sa.Column("params_json", sa.JSON(), nullable=False),
        sa.Column("execution_status", sa.String(), nullable=False, server_default="PENDING"),
        sa.Column("result_json", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "incident_rca_reports",
        sa.Column("run_id", sa.String(), sa.ForeignKey("incident_runs.run_id"), primary_key=True),
        sa.Column("report_markdown", sa.Text(), nullable=False),
        sa.Column("root_cause", sa.Text(), nullable=False),
        sa.Column("resolution", sa.Text(), nullable=False),
        sa.Column("prevention_items_json", sa.JSON(), nullable=True),
        sa.Column("confirmed_by_human", sa.Integer(), server_default="0"),
    )


def downgrade() -> None:
    op.drop_table("incident_rca_reports")
    op.drop_table("incident_actions")
    op.drop_table("incident_approvals")
    op.drop_table("incident_evidence")
    op.drop_table("incident_checkpoints")
    op.drop_table("incident_runs")
