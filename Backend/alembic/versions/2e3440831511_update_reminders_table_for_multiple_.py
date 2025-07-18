"""Update reminders table for multiple scheduled_time and days

Revision ID: 2e3440831511
Revises: 
Create Date: 2025-07-17 22:40:16.225343

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2e3440831511'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('reminders', sa.Column('days', sa.ARRAY(sa.String(length=20)), nullable=True))
    op.drop_column('reminders', 'attempts')
    op.drop_column('reminders', 'reminder_type')
    op.drop_column('reminders', 'channel')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('reminders', sa.Column('channel', sa.VARCHAR(length=20), autoincrement=False, nullable=True))
    op.add_column('reminders', sa.Column('reminder_type', sa.VARCHAR(length=50), autoincrement=False, nullable=True))
    op.add_column('reminders', sa.Column('attempts', sa.INTEGER(), autoincrement=False, nullable=True))
    op.drop_column('reminders', 'days')
    # ### end Alembic commands ###
