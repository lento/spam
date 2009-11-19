from datetime import datetime
from sqlalchemy import *
from migrate import *
#from sqlalchemy.types import Unicode, Integer, DateTime
from sqlalchemy.orm import sessionmaker, relation
from sqlalchemy.ext.declarative import declarative_base

DeclarativeBase = declarative_base(bind=migrate_engine)
metadata = DeclarativeBase.metadata
Session = sessionmaker(bind=migrate_engine)
session = Session()

group_permission_table = Table('auth_group_permission', metadata,
    Column('group_id', Integer, ForeignKey('auth_groups.group_id',
        onupdate="CASCADE", ondelete="CASCADE")),
    Column('permission_id', Integer, ForeignKey('auth_permissions.permission_id',
        onupdate="CASCADE", ondelete="CASCADE"))
)

user_group_table = Table('auth_user_group', metadata,
    Column('user_id', Integer, ForeignKey('auth_users.user_id',
        onupdate="CASCADE", ondelete="CASCADE")),
    Column('group_id', Integer, ForeignKey('auth_groups.group_id',
        onupdate="CASCADE", ondelete="CASCADE"))
)

class Group(DeclarativeBase):
    __tablename__ = 'auth_groups'
    
    group_id = Column(Integer, autoincrement=True, primary_key=True)
    group_name = Column(Unicode(16), unique=True, nullable=False)
    display_name = Column(Unicode(255))
    created = Column(DateTime, default=datetime.now)
    users = relation('User', secondary=user_group_table, backref='groups')


class User(DeclarativeBase):
    __tablename__ = 'auth_users'
    
    user_id = Column(Integer, autoincrement=True, primary_key=True)
    user_name = Column(Unicode(16), unique=True, nullable=False)
    email_address = Column(Unicode(255), unique=True, nullable=False)
    display_name = Column(Unicode(255))
    _password = Column(Unicode(80))
    created = Column(DateTime, default=datetime.now)


class Permission(DeclarativeBase):
    __tablename__ = 'auth_permissions'
    
    permission_id = Column(Integer, autoincrement=True, primary_key=True)
    permission_name = Column(Unicode(16), unique=True, nullable=False)
    description = Column(Unicode(255))
    groups = relation(Group, secondary=group_permission_table,
                      backref='permissions')
    


def upgrade():
    # Upgrade operations go here. Don't create your own engine; use the engine
    # named 'migrate_engine' imported from migrate.
    group_permission_table.create()
    user_group_table.create()
    Group.__table__.create()
    User.__table__.create()
    Permission.__table__.create()
    
    # default users
    admin = User()
    admin.user_name = u'admin'
    admin.display_name = u'SPAM Administrator'
    admin.email_address = u'admin@example.com'
    admin._password = u'4e1b983227e6992278c9fc9346356e40169bef8839441bb9b9ddbb5174a3b89cdc27ad71d79245cd'

    session.add(admin)
    
    # default groups
    administrators = Group()
    administrators.group_name = u'administrators'
    administrators.display_name = u'SPAM Administrators'
    administrators.users.append(admin)
    
    session.add(administrators)
    
    # default permissions
    #perm_user_edit = Permission()
    #perm_user_edit.permission_name = u'edit user'
    #perm_user_edit.description = u'This permission allows to edit a user'
    #perm_user_edit.groups.append(administrators)
    
    #session.add(perm_user_edit)
    
    session.commit()
    session.close()

def downgrade():
    # Operations to reverse the above upgrade go here.
    group_permission_table.drop()
    user_group_table.drop()
    Group.__table__.drop()
    User.__table__.drop()
    Permission.__table__.drop()
