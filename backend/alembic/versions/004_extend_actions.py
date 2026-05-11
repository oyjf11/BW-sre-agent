"""Extend incident_actions with execution tracking fields.

Revision ID: 004
Revises: 003
"""
from alembic import op
import sqlalchemy as sa

revision = "004"
down_revision = "003"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("incident_actions") as batch_op:
        batch_op.add_column(sa.Column("approval_id", sa.String(), nullable=True))
        batch_op.add_column(sa.Column("attempt_no", sa.Integer(), nullable=False, server_default="1"))
        batch_op.add_column(sa.Column("executor_name", sa.String(), nullable=True))
        batch_op.add_column(sa.Column("request_json", sa.JSON(), nullable=True))
        batch_op.add_column(sa.Column("verification_status", sa.String(), nullable=True))
        batch_op.add_column(sa.Column("verification_details_json", sa.JSON(), nullable=True))
        batch_op.add_column(sa.Column("started_at", sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column("completed_at", sa.DateTime(), nullable=True))


def downgrade():
    with op.batch_alter_table("incident_actions") as batch_op:
        batch_op.drop_column("completed_at")
        batch_op.drop_column("started_at")
        batch_op.drop_column("verification_details_json")
        batch_op.drop_column("verification_status")
        batch_op.drop_column("executor_name")
        batch_op.drop_column("attempt_no")
        batch_op.drop_column("approval_id")
        batch_op.drop_column("request_json")
