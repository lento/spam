from datetime import datetime
from sqlalchemy import *
from migrate import *
#from sqlalchemy.types import Unicode, Integer, DateTime
from sqlalchemy.orm import sessionmaker, relation
from sqlalchemy.ext.declarative import declarative_base

metadata = MetaData()
DeclarativeBase = declarative_base(bind=migrate_engine, metadata=metadata)

# This is the association table for the many-to-many relationship between
# groups and permissions. This is required by repoze.what.
groups_permissions_table = Table('__groups_permissions', metadata,
    Column('group_id', Integer, ForeignKey('groups.group_id',
        onupdate="CASCADE", ondelete="CASCADE")),
    Column('permission_id', Integer, ForeignKey('permissions.permission_id',
        onupdate="CASCADE", ondelete="CASCADE"))
)

# This is the association table for the many-to-many relationship between
# groups and members - this is, the memberships. It's required by repoze.what.
users_groups_table = Table('__users_groups', metadata,
    Column('user_id', Integer, ForeignKey('users.user_id',
        onupdate="CASCADE", ondelete="CASCADE")),
    Column('group_id', Integer, ForeignKey('groups.group_id',
        onupdate="CASCADE", ondelete="CASCADE"))
)

class Group(DeclarativeBase):
    """
    Group definition for :mod:`repoze.what`.
    
    Only the ``group_name`` column is required by :mod:`repoze.what`.
    """
    __tablename__ = 'groups'
    
    # Columns
    group_id = Column(Unicode(40), primary_key=True)
    group_name = Column(Unicode(16), unique=True, nullable=False)
    display_name = Column(Unicode(255))
    created = Column(DateTime, default=datetime.now)


class User(DeclarativeBase):
    """
    User definition.
    
    This is the user definition used by :mod:`repoze.who`, which requires at
    least the ``user_name`` column.
    """
    __tablename__ = 'users'
    
    # Columns
    user_id = Column(Unicode(40), primary_key=True)
    user_name = Column(Unicode(16), unique=True, nullable=False)
    email_address = Column(Unicode(255), unique=True)
    display_name = Column(Unicode(255))
    _password = Column(Unicode(80))
    created = Column(DateTime, default=datetime.now)


class Permission(DeclarativeBase):
    """
    Permission definition for :mod:`repoze.what`.
    
    Only the ``permission_name`` column is required by :mod:`repoze.what`.
    """
    __tablename__ = 'permissions'
    
    # Columns
    permission_id = Column(Unicode(40), primary_key=True)
    permission_name = Column(Unicode(16), unique=True, nullable=False)
    description = Column(Unicode(255))


def upgrade():
    # Upgrade operations go here. Don't create your own engine; use the engine
    # named 'migrate_engine' imported from migrate.
    groups_permissions_table.create()
    users_groups_table.create()
    Group.__table__.create()
    User.__table__.create()
    Permission.__table__.create()
    
def downgrade():
    # Operations to reverse the above upgrade go here.
    groups_permissions_table.drop()
    users_groups_table.drop()
    Group.__table__.drop()
    User.__table__.drop()
    Permission.__table__.drop()

