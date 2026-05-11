"""Add reason, expected_impact, rollback_plan to incident_approvals.

Revision ID: 006
Revises: 005
"""
from alembic import op
import sqlalchemy as sa

revision = "006"
down_revision = "005"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("incident_approvals") as batch_op:
        batch_op.add_column(sa.Column("reason", sa.Text(), nullable=True))
        batch_op.add_column(sa.Column("expected_impact", sa.Text(), nullable=True))
        batch_op.add_column(sa.Column("rollback_plan", sa.Text(), nullable=True))


def downgrade():
    with op.batch_alter_table("incident_approvals") as batch_op:
        batch_op.drop_column("rollback_plan")
        batch_op.drop_column("expected_impact")
        batch_op.drop_column("reason")
