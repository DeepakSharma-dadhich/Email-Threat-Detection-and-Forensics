"""create email records

Revision ID: 0001
Revises:
Create Date: 2026-09-01
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "0001"
down_revision: Union[str, Sequence[str], None] = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "email_records",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("source_type", sa.String(length=32), nullable=False, index=True),
        sa.Column("source_message_id", sa.Text(), nullable=True),
        sa.Column("original_filename", sa.Text(), nullable=True),
        sa.Column("message_id", sa.Text(), nullable=True, index=True),
        sa.Column("subject", sa.Text(), nullable=True),
        sa.Column("from_address", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("reply_to", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("return_path", sa.Text(), nullable=True),
        sa.Column("to_addresses", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("cc_addresses", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("bcc_addresses", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("received_at", sa.DateTime(timezone=True), nullable=True, index=True),
        sa.Column("headers", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("body_text", sa.Text(), nullable=True),
        sa.Column("body_html", sa.Text(), nullable=True),
        sa.Column("attachments", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("raw_sha256", sa.String(length=64), nullable=False),
        sa.Column("raw_storage_key", sa.Text(), nullable=False),
        sa.Column("raw_size_bytes", sa.BigInteger(), nullable=False),
        sa.Column("parse_warnings", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
   

def downgrade() -> None:
     op.drop_table("email_records")
