from datetime import datetime
from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from migrate import *

metadata = MetaData()
DeclarativeBase = declarative_base(metadata=metadata)

# This is the association table for the many-to-many relationship between
# groups and permissions. This is required by repoze.what.
groups_permissions_table = Table('__groups_permissions', metadata,
    Column('group_id', Unicode(40), ForeignKey('groups.group_id',
        onupdate="CASCADE", ondelete="CASCADE")),
    Column('permission_id', Unicode(40), ForeignKey('permissions.permission_id',
        onupdate="CASCADE", ondelete="CASCADE"))
)

# This is the association table for the many-to-many relationship between
# groups and members - this is, the memberships. It's required by repoze.what.
users_groups_table = Table('__users_groups', metadata,
    Column('user_id', Unicode(40), ForeignKey('users.user_id',
        onupdate="CASCADE", ondelete="CASCADE")),
    Column('group_id', Unicode(40), ForeignKey('groups.group_id',
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


def upgrade(migrate_engine):
    """operations to upgrade the db"""
    metadata.bind = migrate_engine

    Group.__table__.create()
    User.__table__.create()
    Permission.__table__.create()
    groups_permissions_table.create()
    users_groups_table.create()
    
def downgrade(migrate_engine):
    """operations to reverse the above upgrade"""
    metadata.bind = migrate_engine

    users_groups_table.drop()
    groups_permissions_table.drop()
    Permission.__table__.drop()
    User.__table__.drop()
    Group.__table__.drop()

