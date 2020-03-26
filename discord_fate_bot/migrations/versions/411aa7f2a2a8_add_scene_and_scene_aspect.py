"""Add scene and scene_aspect

Revision ID: 411aa7f2a2a8
Revises: 
Create Date: 2020-03-23 23:19:09.324215

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '411aa7f2a2a8'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'scene',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('channel_id', sa.Integer(), nullable=False),
        sa.Column('description', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('id', name=op.f('pk__scene')),
        sa.UniqueConstraint('channel_id', name=op.f('uq__scene__channel_id'))
    )
    op.create_table(
        'scene_aspects',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('scene_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.ForeignKeyConstraint(['scene_id'], ['scene.id'], name=op.f('fk__scene_aspects__scene_id__scene')),
        sa.PrimaryKeyConstraint('id', name=op.f('pk__scene_aspects'))
    )


def downgrade():
    op.drop_table('scene_aspects')
    op.drop_table('scene')

