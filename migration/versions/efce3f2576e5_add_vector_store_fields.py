"""add vector store fields

Revision ID: efce3f2576e5
Revises: 
Create Date: 2026-08-04 16:42:32.672130

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'efce3f2576e5'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    with op.batch_alter_table(
        "document_chunks"
    ) as batch_op:
        batch_op.add_column(
            sa.Column(
                "vector_id",
                sa.String(),
                nullable=True,
            )
        )

        batch_op.add_column(
            sa.Column(
                "vector_store",
                sa.String(),
                nullable=True,
            )
        )

        batch_op.add_column(
            sa.Column(
                "vector_store_status",
                sa.String(),
                nullable=True,
            )
        )

        batch_op.add_column(
            sa.Column(
                "vector_store_error",
                sa.Text(),
                nullable=True,
            )
        )

        batch_op.add_column(
            sa.Column(
                "indexed_at",
                sa.DateTime(),
                nullable=True,
            )
        )

    op.execute(
        """
        UPDATE document_chunks
        SET vector_store_status = 'pending'
        WHERE vector_store_status IS NULL
        """
    )

    with op.batch_alter_table(
        "document_chunks"
    ) as batch_op:
        batch_op.alter_column(
            "vector_store_status",
            existing_type=sa.String(),
            nullable=False,
        )

        batch_op.create_unique_constraint(
            "uq_document_chunks_vector_id",
            ["vector_id"],
        )


def downgrade() -> None:
    with op.batch_alter_table(
        "document_chunks"
    ) as batch_op:
        batch_op.drop_constraint(
            "uq_document_chunks_vector_id",
            type_="unique",
        )

        batch_op.drop_column("indexed_at")
        batch_op.drop_column("vector_store_error")
        batch_op.drop_column("vector_store_status")
        batch_op.drop_column("vector_store")
        batch_op.drop_column("vector_id")