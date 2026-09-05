"""create email lifecycle tables

Revision ID: 0003
Revises: 0002_create_analysis_records
Create Date: 2026-09-02
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from sqlalchemy.dialects import postgresql


revision: str = "0003"

down_revision: Union[
    str,
    Sequence[str],
    None,
] = "0002_create_analysis_records"

branch_labels = None
depends_on = None


def upgrade() -> None:

    op.create_table(
        "email_lifecycle_states",

        sa.Column(
            "state_id",
            postgresql.UUID(
                as_uuid=True
            ),
            nullable=False,
        ),

        sa.Column(
            "email_id",
            postgresql.UUID(
                as_uuid=True
            ),
            nullable=False,
        ),

        sa.Column(
            "status",
            sa.String(
                length=32
            ),
            nullable=False,
        ),

        sa.Column(
            "latest_analysis_id",
            postgresql.UUID(
                as_uuid=True
            ),
            nullable=True,
        ),

        sa.Column(
            "updated_by",
            sa.String(
                length=32
            ),
            nullable=False,
        ),

        sa.Column(
            "updated_at",
            sa.DateTime(
                timezone=True
            ),
            nullable=False,
        ),

        sa.ForeignKeyConstraint(
            ["email_id"],
            ["email_records.id"],
            ondelete="CASCADE",
        ),

        sa.ForeignKeyConstraint(
            ["latest_analysis_id"],
            ["analysis_records.analysis_id"],
            ondelete="SET NULL",
        ),

        sa.PrimaryKeyConstraint(
            "state_id"
        ),

        sa.UniqueConstraint(
            "email_id",
            name=(
                "uq_email_lifecycle_states_email_id"
            ),
        ),
    )

    op.create_index(
        "ix_email_lifecycle_states_email_id",
        "email_lifecycle_states",
        ["email_id"],
        unique=False,
    )

    op.create_table(
        "email_action_history",

        sa.Column(
            "action_id",
            postgresql.UUID(
                as_uuid=True
            ),
            nullable=False,
        ),

        sa.Column(
            "email_id",
            postgresql.UUID(
                as_uuid=True
            ),
            nullable=False,
        ),

        sa.Column(
            "analysis_id",
            postgresql.UUID(
                as_uuid=True
            ),
            nullable=True,
        ),

        sa.Column(
            "action",
            sa.String(
                length=64
            ),
            nullable=False,
        ),

        sa.Column(
            "previous_status",
            sa.String(
                length=32
            ),
            nullable=True,
        ),

        sa.Column(
            "new_status",
            sa.String(
                length=32
            ),
            nullable=False,
        ),

        sa.Column(
            "actor_type",
            sa.String(
                length=32
            ),
            nullable=False,
        ),

        sa.Column(
            "reason",
            sa.Text(),
            nullable=True,
        ),

        sa.Column(
            "created_at",
            sa.DateTime(
                timezone=True
            ),
            nullable=False,
        ),

        sa.ForeignKeyConstraint(
            ["email_id"],
            ["email_records.id"],
            ondelete="CASCADE",
        ),

        sa.ForeignKeyConstraint(
            ["analysis_id"],
            ["analysis_records.analysis_id"],
            ondelete="SET NULL",
        ),

        sa.PrimaryKeyConstraint(
            "action_id"
        ),
    )

    op.create_index(
        "ix_email_action_history_email_id",
        "email_action_history",
        ["email_id"],
        unique=False,
    )

    op.create_index(
        "ix_email_action_history_created_at",
        "email_action_history",
        ["created_at"],
        unique=False,
    )


def downgrade() -> None:

    op.drop_index(
        "ix_email_action_history_created_at",
        table_name="email_action_history",
    )

    op.drop_index(
        "ix_email_action_history_email_id",
        table_name="email_action_history",
    )

    op.drop_table(
        "email_action_history"
    )

    op.drop_index(
        "ix_email_lifecycle_states_email_id",
        table_name="email_lifecycle_states",
    )

    op.drop_table(
        "email_lifecycle_states"
    )