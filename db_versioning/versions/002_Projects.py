from datetime import datetime
from sqlalchemy import *
from migrate import *
from sqlalchemy.orm import sessionmaker, relation
from sqlalchemy.ext.declarative import declarative_base

metadata = MetaData()
DeclarativeBase = declarative_base(bind=migrate_engine, metadata=metadata)

# Existing classes and tables to be used in relations
users = Table('users', metadata, autoload=True)

# New classes and tables
projects_admins_table = Table('__projects_admins', metadata,
    Column('project_id', Unicode(10), ForeignKey('projects.id',
                                    onupdate="CASCADE", ondelete="CASCADE")),
    Column('user_id', Integer, ForeignKey('users.user_id',
                                    onupdate="CASCADE", ondelete="CASCADE"))
)

class Project(DeclarativeBase):
    __tablename__ = 'projects'
    
    id = Column(Unicode(10), primary_key=True)
    name = Column(Unicode(40))
    description = Column(Unicode)
    modified = Column(DateTime, default=datetime.now)
    archived = Column(Boolean, default=False)


def upgrade():
    # Upgrade operations go here. Don't create your own engine; use the engine
    # named 'migrate_engine' imported from migrate.
    projects_admins_table.create()
    Project.__table__.create()

def downgrade():
    # Operations to reverse the above upgrade go here.
    projects_admins_table.drop()
    Project.__table__.drop()

