"""extend incident_runs + add incident_run_events table

Revision ID: 002
Revises: 001
Create Date: 2026-03-28
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Extend incident_runs
    with op.batch_alter_table("incident_runs") as batch_op:
        batch_op.add_column(sa.Column("current_node", sa.String(), nullable=True))
        batch_op.add_column(sa.Column("input_source", sa.String(), nullable=True))
        batch_op.add_column(sa.Column("schema_version", sa.Integer(), nullable=False, server_default="1"))
        batch_op.add_column(sa.Column("step_count", sa.Integer(), nullable=False, server_default="0"))
        batch_op.add_column(sa.Column("last_error_code", sa.String(), nullable=True))
        batch_op.add_column(sa.Column("last_error_message", sa.Text(), nullable=True))
        batch_op.add_column(sa.Column("started_at", sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column("requires_human", sa.Integer(), nullable=False, server_default="0"))
        batch_op.add_column(sa.Column("summary_json", sa.JSON(), nullable=True))

    # New table: incident_run_events
    op.create_table(
        "incident_run_events",
        sa.Column("event_id", sa.String(), primary_key=True),
        sa.Column("run_id", sa.String(), sa.ForeignKey("incident_runs.run_id"), nullable=False),
        sa.Column("ts", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("level", sa.String(), nullable=False, server_default="INFO"),
        sa.Column("type", sa.String(), nullable=False),
        sa.Column("node_name", sa.String(), nullable=True),
        sa.Column("message", sa.Text(), nullable=True),
        sa.Column("data_json", sa.JSON(), nullable=True),
    )
    op.create_index("ix_incident_run_events_run_id", "incident_run_events", ["run_id"])


def downgrade() -> None:
    op.drop_index("ix_incident_run_events_run_id", table_name="incident_run_events")
    op.drop_table("incident_run_events")

    with op.batch_alter_table("incident_runs") as batch_op:
        batch_op.drop_column("summary_json")
        batch_op.drop_column("requires_human")
        batch_op.drop_column("started_at")
        batch_op.drop_column("last_error_message")
        batch_op.drop_column("last_error_code")
        batch_op.drop_column("step_count")
        batch_op.drop_column("schema_version")
        batch_op.drop_column("input_source")
        batch_op.drop_column("current_node")
