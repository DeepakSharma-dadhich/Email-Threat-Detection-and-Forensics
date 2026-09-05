"""create analysis records table

Revision ID: 0002_create_analysis_records
Revises: 0001_create_email_records
Create Date: 2026-09-02
"""

from typing import (
    Sequence,
    Union,
)

from alembic import op
import sqlalchemy as sa

from sqlalchemy.dialects import postgresql


revision: str = "0002_create_analysis_records"

down_revision: Union[
    str,
    Sequence[str],
    None,
] = "0001"

branch_labels: Union[
    str,
    Sequence[str],
    None,
] = None

depends_on: Union[
    str,
    Sequence[str],
    None,
] = None


def upgrade() -> None:

    op.create_table(
        "analysis_records",

        sa.Column(
            "analysis_id",
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
            "job_status",
            sa.String(
                length=32
            ),
            nullable=False,
        ),

        sa.Column(
            "aggregate_score",
            sa.Integer(),
            nullable=True,
        ),

        sa.Column(
            "verdict",
            sa.String(
                length=32
            ),
            nullable=True,
        ),

        sa.Column(
            "recommended_action",
            sa.String(
                length=64
            ),
            nullable=True,
        ),

        sa.Column(
            "browser_isolation_recommended",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),

        sa.Column(
            "module_results",
            postgresql.JSONB(
                astext_type=sa.Text()
            ),
            nullable=False,
        ),

        sa.Column(
            "result_data",
            postgresql.JSONB(
                astext_type=sa.Text()
            ),
            nullable=False,
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

        sa.PrimaryKeyConstraint(
            "analysis_id"
        ),
    )

    op.create_index(
        "ix_analysis_records_email_id",
        "analysis_records",
        ["email_id"],
        unique=False,
    )

    op.create_index(
        "ix_analysis_records_created_at",
        "analysis_records",
        ["created_at"],
        unique=False,
    )


def downgrade() -> None:

    op.drop_index(
        "ix_analysis_records_created_at",
        table_name="analysis_records",
    )

    op.drop_index(
        "ix_analysis_records_email_id",
        table_name="analysis_records",
    )

    op.drop_table(
        "analysis_records"
    )