from datetime import datetime
from sqlalchemy import Table, Column, MetaData, and_
from sqlalchemy import UniqueConstraint, ForeignKeyConstraint, ForeignKey
from sqlalchemy.types import Unicode, UnicodeText, DateTime, Integer
from sqlalchemy.orm import relation, backref
from migrate import *
from sqlalchemy.ext.declarative import declarative_base

migrate_metadata = MetaData()
DeclarativeBase = declarative_base(bind=migrate_engine,
                                                    metadata=migrate_metadata)


# Existing classes and tables to be used in relations
class AssetContainer(DeclarativeBase):
    """Base class for object containers"""
    __tablename__ = 'asset_containers'
        
    id = Column(Integer, primary_key=True)
    proj_id = Column(Unicode(10))
    type = Column(Unicode(20))
    __mapper_args__ = {'polymorphic_on': type}


# New classes and tables
class LibraryGroup(AssetContainer):
    """Library group"""
    __tablename__ = "library_groups"
    __table_args__ = (UniqueConstraint('proj_id', 'parent_id', 'name'),
                      ForeignKeyConstraint(['id', 'proj_id'],
                          ['asset_containers.id', 'asset_containers.proj_id']),
                      ForeignKeyConstraint(['parent_id', 'proj_id'],
                          ['library_groups.id', 'library_groups.proj_id']),
                      {})
    __mapper_args__ = {'polymorphic_identity': 'library_group'}
    
    id = Column(Integer, primary_key=True)
    proj_id = Column(Unicode(10))
    parent_id = Column(Integer)
    name = Column(Unicode(40))
    description = Column(UnicodeText)
    #note_id = Column(None, ForeignKey('notes_associations.assoc_id'))


def upgrade():
    # Upgrade operations go here. Don't create your own engine; use the engine
    # named 'migrate_engine' imported from migrate.
    LibraryGroup.__table__.create()

def downgrade():
    # Operations to reverse the above upgrade go here.
    LibraryGroup.__table__.drop()

