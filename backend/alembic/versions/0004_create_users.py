from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


revision: str = "0004"
down_revision: str | None = "0003"

branch_labels: (
    str
    | Sequence[str]
    | None
) = None

depends_on: (
    str
    | Sequence[str]
    | None
) = None


def upgrade() -> None:

    op.create_table(
        "users",

        sa.Column(
            "id",
            postgresql.UUID(
                as_uuid=True
            ),
            nullable=False,
        ),

        sa.Column(
            "name",
            sa.String(
                length=120
            ),
            nullable=False,
        ),

        sa.Column(
            "email",
            sa.String(
                length=320
            ),
            nullable=False,
        ),

        sa.Column(
            "password_hash",
            sa.String(
                length=255
            ),
            nullable=False,
        ),

        sa.Column(
            "is_active",
            sa.Boolean(),
            nullable=False,
            server_default=sa.true(),
        ),

        sa.Column(
            "created_at",
            sa.DateTime(
                timezone=True
            ),
            nullable=False,
            server_default=sa.func.now(),
        ),

        sa.Column(
            "updated_at",
            sa.DateTime(
                timezone=True
            ),
            nullable=False,
            server_default=sa.func.now(),
        ),

        sa.PrimaryKeyConstraint(
            "id"
        ),

        sa.UniqueConstraint(
            "email"
        ),
    )

    op.create_index(
        "ix_users_email",
        "users",
        [
            "email"
        ],
        unique=True,
    )


def downgrade() -> None:

    op.drop_index(
        "ix_users_email",
        table_name="users",
    )

    op.drop_table(
        "users"
    )