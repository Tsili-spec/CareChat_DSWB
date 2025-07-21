"""
Remove sentiment_score and status from feedback table
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '20250717_remove_sentiment_score_status_from_feedback'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    with op.batch_alter_table('feedback') as batch_op:
        batch_op.drop_column('sentiment_score')
        batch_op.drop_column('status')

def downgrade():
    with op.batch_alter_table('feedback') as batch_op:
        batch_op.add_column(sa.Column('sentiment_score', sa.Float))
        batch_op.add_column(sa.Column('status', sa.String(20)))
