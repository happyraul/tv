"""create series, episodes, images, userimages

Revision ID: 36674b393934
Revises: 3fa887d26ab1
Create Date: 2014-08-17 09:33:04.741713

"""

# revision identifiers, used by Alembic.
revision = '36674b393934'
down_revision = '3fa887d26ab1'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('series',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('air_day', sa.Enum('su', 'mo', 'tu', 'we', 'th',
                              'fr', 'sa', name='day_of_week'), nullable=True),
                    sa.Column('air_time', sa.Time(), nullable=True),
                    sa.Column('first_aired', sa.Date(), nullable=True),
                    sa.Column('network', sa.String(), nullable=True),
                    sa.Column('overview', sa.String(), nullable=True),
                    sa.Column('rating', sa.Numeric(precision=3, scale=1),
                              nullable=True),
                    sa.Column('rating_count', sa.Integer(), nullable=True),
                    sa.Column('runtime', sa.Integer(), nullable=True),
                    sa.Column('name', sa.String(), nullable=False),
                    sa.Column('status', sa.Enum('c', 'e', 'h', 'o',
                              name='status'), nullable=True),
                    sa.Column('last_updated', sa.DateTime(), nullable=True),
                    sa.PrimaryKeyConstraint('id'))

    op.create_table('episodes',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('series_id', sa.Integer(), nullable=False),
                    sa.Column('season', sa.Integer(), nullable=True),
                    sa.Column('episode_number', sa.Integer(), nullable=True),
                    sa.Column('name', sa.String(), nullable=True),
                    sa.Column('overview', sa.String(), nullable=True),
                    sa.Column('rating', sa.Numeric(precision=3, scale=1),
                              nullable=True),
                    sa.Column('rating_count', sa.Integer(), nullable=True),
                    sa.Column('air_date', sa.Date(), nullable=True),
                    sa.ForeignKeyConstraint(['series_id'], ['series.id']),
                    sa.PrimaryKeyConstraint('id'))

    op.create_table('images',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('episode_id', sa.Integer(), nullable=True),
                    sa.Column('series_id', sa.Integer(), nullable=False),
                    sa.Column('source', sa.String(), nullable=False),
                    sa.Column('key', sa.String(), nullable=False),
                    sa.Column('type', sa.Enum('poster', 'series', 'fanart',
                              'season', name='image_types'), nullable=False),
                    sa.ForeignKeyConstraint(['episode_id'], ['episodes.id']),
                    sa.ForeignKeyConstraint(['series_id'], ['series.id']),
                    sa.PrimaryKeyConstraint('id'),
                    sa.UniqueConstraint('key'),
                    sa.UniqueConstraint('source'))

    op.create_table('user_images',
                    sa.Column('user_id', sa.Integer(), nullable=False),
                    sa.Column('image_id', sa.Integer(), nullable=False),
                    sa.ForeignKeyConstraint(['image_id'], ['images.id'], ),
                    sa.ForeignKeyConstraint(['user_id'], ['users.id']))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('user_images')
    op.drop_table('images')
    op.drop_table('episodes')
    op.drop_table('series')
    sa.dialects.postgresql.ENUM(name='day_of_week').drop(op.get_bind())
    sa.dialects.postgresql.ENUM(name='status').drop(op.get_bind())
    sa.dialects.postgresql.ENUM(name='image_types').drop(op.get_bind())
    ### end Alembic commands ###
