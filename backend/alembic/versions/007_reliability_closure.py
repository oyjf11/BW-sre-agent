"""Add reliability closure fields: halted_at_node, terminal_reason_json, RCA fields.

Revision ID: 007
Revises: 006
"""
from alembic import op
import sqlalchemy as sa

revision = "007"
down_revision = "006"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("incident_runs") as batch_op:
        batch_op.add_column(sa.Column("halted_at_node", sa.String(), nullable=True))
        batch_op.add_column(sa.Column("terminal_reason_json", sa.JSON(), nullable=True))

    with op.batch_alter_table("incident_rca_reports") as batch_op:
        batch_op.add_column(sa.Column("root_cause_status", sa.String(), nullable=True))
        batch_op.add_column(sa.Column("candidate_hypotheses_json", sa.JSON(), nullable=True))
        batch_op.add_column(sa.Column("automation_outcome_json", sa.JSON(), nullable=True))
        batch_op.add_column(sa.Column("manual_next_steps_json", sa.JSON(), nullable=True))


def downgrade():
    with op.batch_alter_table("incident_rca_reports") as batch_op:
        batch_op.drop_column("manual_next_steps_json")
        batch_op.drop_column("automation_outcome_json")
        batch_op.drop_column("candidate_hypotheses_json")
        batch_op.drop_column("root_cause_status")

    with op.batch_alter_table("incident_runs") as batch_op:
        batch_op.drop_column("terminal_reason_json")
        batch_op.drop_column("halted_at_node")
