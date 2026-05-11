"""add incident_tool_audits table

Revision ID: 003
Revises: 002
Create Date: 2026-03-28
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "003"
down_revision: Union[str, None] = "002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "incident_tool_audits",
        sa.Column("audit_id", sa.String(), primary_key=True),
        sa.Column("run_id", sa.String(), sa.ForeignKey("incident_runs.run_id"), nullable=False),
        sa.Column("tool_name", sa.String(), nullable=False),
        sa.Column("adapter_mode", sa.String(), nullable=False),
        sa.Column("request_json", sa.JSON(), nullable=True),
        sa.Column("response_json", sa.JSON(), nullable=True),
        sa.Column("success", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("latency_ms", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_incident_tool_audits_run_id", "incident_tool_audits", ["run_id"])


def downgrade() -> None:
    op.drop_index("ix_incident_tool_audits_run_id", table_name="incident_tool_audits")
    op.drop_table("incident_tool_audits")
