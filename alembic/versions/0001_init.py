from alembic import op
import sqlalchemy as sa

revision = '0001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'device',
        sa.Column('mac', sa.String(), primary_key=True),
        sa.Column('vendor', sa.String()),
        sa.Column('first_seen', sa.DateTime()),
        sa.Column('last_seen', sa.DateTime()),
        sa.Column('rssi_history', sa.String()),
    )
    op.create_table(
        'rawpacket',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('phy', sa.String()),
        sa.Column('channel', sa.Integer()),
        sa.Column('rssi', sa.Integer()),
        sa.Column('address', sa.String()),
        sa.Column('payload', sa.LargeBinary()),
    )
    op.create_table(
        'capturesession',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('start_time', sa.DateTime(), nullable=False),
        sa.Column('end_time', sa.DateTime()),
    )
    op.create_table(
        'decodedevent',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('session_id', sa.Integer(), sa.ForeignKey('capturesession.id')),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('event_type', sa.String(), nullable=False),
        sa.Column('data', sa.String()),
    )
    op.create_table(
        'alertrule',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('pattern', sa.String(), nullable=False),
        sa.Column('threshold', sa.Integer()),
    )


def downgrade():
    op.drop_table('alertrule')
    op.drop_table('decodedevent')
    op.drop_table('capturesession')
    op.drop_table('rawpacket')
    op.drop_table('device')
