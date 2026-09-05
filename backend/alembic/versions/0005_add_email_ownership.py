from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


revision: str = "0005"
down_revision: str | None = "0004"

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
    op.add_column(
        "email_records",
        sa.Column(
            "user_id",
            postgresql.UUID(
                as_uuid=True
            ),
            nullable=True,
        ),
    )

    op.create_foreign_key(
        "fk_email_records_user_id_users",
        "email_records",
        "users",
        [
            "user_id"
        ],
        [
            "id"
        ],
        ondelete="CASCADE",
    )

    op.create_index(
        "ix_email_records_user_id",
        "email_records",
        [
            "user_id"
        ],
        unique=False,
    )

    connection = op.get_bind()

    user_count = connection.execute(
        sa.text(
            """
            SELECT COUNT(*)
            FROM users
            """
        )
    ).scalar()

    if user_count == 1:
        connection.execute(
            sa.text(
                """
                UPDATE email_records
                SET user_id = (
                    SELECT id
                    FROM users
                    LIMIT 1
                )
                WHERE user_id IS NULL
                """
            )
        )


def downgrade() -> None:
    op.drop_index(
        "ix_email_records_user_id",
        table_name="email_records",
    )

    op.drop_constraint(
        "fk_email_records_user_id_users",
        "email_records",
        type_="foreignkey",
    )

    op.drop_column(
        "email_records",
        "user_id",
    )