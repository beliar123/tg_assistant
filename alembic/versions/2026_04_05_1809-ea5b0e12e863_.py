"""empty message

Revision ID: ea5b0e12e863
Revises:
Create Date: 2026-04-05 18:09:15.710862

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = 'ea5b0e12e863'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    sa.Enum('DAILY', 'WEEKLY', 'MONTHLY', 'SIXMONTH', 'YEARLY', name='event_repeat_intervals').create(op.get_bind())
    op.create_table('user',
    sa.Column('username', sa.String(length=64), nullable=False),
    sa.Column('hashed_password', sa.String(length=255), nullable=False),
    sa.Column('telegram_id', sa.Integer(), nullable=True),
    sa.Column('chat_id', sa.Integer(), nullable=True),
    sa.Column('name', sa.String(length=32), nullable=False),
    sa.Column('lastname', sa.String(length=32), nullable=True),
    sa.Column('email', sa.String(length=255), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_user')),
    sa.UniqueConstraint('telegram_id', name=op.f('uq_user_telegram_id')),
    sa.UniqueConstraint('username', name=op.f('uq_user_username'))
    )
    op.create_table('event',
    sa.Column('event_datetime', sa.DateTime(timezone=True), nullable=False),
    sa.Column('description', sa.Text(), nullable=False),
    sa.Column('repeat_interval', postgresql.ENUM('DAILY', 'WEEKLY', 'MONTHLY', 'SIXMONTH', 'YEARLY', name='event_repeat_intervals', create_type=False), nullable=True),
    sa.Column('message_count', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], name=op.f('fk_event_user_id_user')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_event'))
    )


def downgrade() -> None:
    op.drop_table('event')
    op.drop_table('user')
    sa.Enum('DAILY', 'WEEKLY', 'MONTHLY', 'SIXMONTH', 'YEARLY', name='event_repeat_intervals').drop(op.get_bind())
