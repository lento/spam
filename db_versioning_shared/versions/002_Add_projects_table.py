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


# Existing classes and tables to be used in relations
class User(DeclarativeBase):
    __tablename__ = 'auth_users'
    
    user_id = Column(Integer, autoincrement=True, primary_key=True)
    user_name = Column(Unicode(16), unique=True, nullable=False)
    email_address = Column(Unicode(255), unique=True, nullable=False)
    display_name = Column(Unicode(255))
    _password = Column(Unicode(80))
    created = Column(DateTime, default=datetime.now)


# New classes and tables
project_user_table = Table('__project_user', metadata,
    Column('project_id', Integer, ForeignKey('projects.id',
        onupdate="CASCADE", ondelete="CASCADE")),
    Column('user_id', Integer, ForeignKey('auth_users.user_id',
        onupdate="CASCADE", ondelete="CASCADE"))
)

project_admin_table = Table('__project_admin', metadata,
    Column('project_id', Integer, ForeignKey('projects.id',
        onupdate="CASCADE", ondelete="CASCADE")),
    Column('user_id', Integer, ForeignKey('auth_users.user_id',
        onupdate="CASCADE", ondelete="CASCADE"))
)

class Project(DeclarativeBase):
    __tablename__ = 'projects'
    
    id = Column(Integer, autoincrement=True, primary_key=True)
    nick = Column(Unicode(16), unique=True, nullable=False)
    name = Column(Unicode(255))
    description = Column(Unicode)
    created = Column(DateTime, default=datetime.now)


def upgrade():
    # Upgrade operations go here. Don't create your own engine; use the engine
    # named 'migrate_engine' imported from migrate.
    project_user_table.create()
    project_admin_table.create()
    Project.__table__.create()

def downgrade():
    # Operations to reverse the above upgrade go here.
    project_user_table.drop()
    project_admin_table.drop()
    Project.__table__.drop()

