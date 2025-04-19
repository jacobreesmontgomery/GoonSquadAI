"""Add suffer score and perceived exertion to activities

Revision ID: f7cbaafddf65
Revises: 
Create Date: 2025-04-18 20:53:26.228526

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f7cbaafddf65'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema to add new columns."""
    # Add the two new columns to the existing activities table
    op.add_column('activities', 
                  sa.Column('suffer_score', sa.Float(), nullable=True), 
                  schema='strava_api')
    op.add_column('activities', 
                  sa.Column('perceived_exertion', sa.Float(), nullable=True), 
                  schema='strava_api')


def downgrade() -> None:
    """Downgrade schema by removing added columns."""
    # Remove the two columns that were added
    op.drop_column('activities', 'suffer_score', schema='strava_api')
    op.drop_column('activities', 'perceived_exertion', schema='strava_api')
