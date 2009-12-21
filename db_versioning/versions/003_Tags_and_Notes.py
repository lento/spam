from datetime import datetime
from sqlalchemy import Table, MetaData, and_
from sqlalchemy import UniqueConstraint, Column, ForeignKey
from sqlalchemy.types import Unicode, UnicodeText, DateTime, Integer, Boolean
from sqlalchemy.types import String
from sqlalchemy.orm import relation, backref
from migrate import migrate_engine
from migrate.changeset import schema
from migrate.changeset.constraint import ForeignKeyConstraint
from sqlalchemy.ext.declarative import declarative_base

migrate_metadata = MetaData()
DeclarativeBase = declarative_base(bind=migrate_engine,
                                                    metadata=migrate_metadata)


# Existing classes and tables to be used in relations


# New classes and tables
class Taggable(DeclarativeBase):
    __tablename__ = 'taggables'
    
    # Columns
    id = Column(Integer, autoincrement=True, primary_key=True)
    proj_id = Column(Unicode(10))
    association_type = Column(Unicode(50))


class Tag(DeclarativeBase):
    __tablename__ = 'tags'
    __table_args__ = (ForeignKeyConstraint(['taggable_id', 'proj_id'],
                                        ['taggables.id', 'taggables.proj_id']),
                      {})
    
    # Columns
    id = Column(Integer, autoincrement=True, primary_key=True)
    proj_id = Column(Unicode(10))
    taggable_id = Column(Integer)
    name = Column(UnicodeText)
    created = Column(DateTime, default=datetime.now)
    

class Annotable(DeclarativeBase):
    __tablename__ = 'annotables'
    
    # Columns
    id = Column(Integer, autoincrement=True, primary_key=True)
    proj_id = Column(Unicode(10))
    association_type = Column(Unicode(50))


class Note(DeclarativeBase):
    __tablename__ = 'notes'
    __table_args__ = (ForeignKeyConstraint(['annotable_id', 'proj_id'],
                                    ['annotables.id', 'annotables.proj_id']),
                      {})
    
    # Columns
    id = Column(Integer, autoincrement=True, primary_key=True)
    proj_id = Column(Unicode(10))
    annotable_id = Column(Integer)
    user_id = Column(Integer)
    text = Column(UnicodeText)
    created = Column(DateTime, default=datetime.now)
    sticky = Column(Boolean, default=False)


def upgrade():
    # Upgrade operations go here. Don't create your own engine; use the engine
    # named 'migrate_engine' imported from migrate.
    Taggable.__table__.create()
    Tag.__table__.create()
    Annotable.__table__.create()
    Note.__table__.create()

def downgrade():
    # Operations to reverse the above upgrade go here.
    Taggable.__table__.drop()
    Tag.__table__.drop()
    Annotable.__table__.drop()
    Note.__table__.drop()
    

