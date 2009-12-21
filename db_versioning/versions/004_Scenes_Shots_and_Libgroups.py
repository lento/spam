from datetime import datetime
from sqlalchemy import Table, Column, MetaData
from sqlalchemy import UniqueConstraint, ForeignKeyConstraint, ForeignKey
from sqlalchemy.types import Unicode, UnicodeText, DateTime, Integer
from sqlalchemy.orm import relation, backref
from migrate import *
from sqlalchemy.ext.declarative import declarative_base

migrate_metadata = MetaData()
DeclarativeBase = declarative_base(bind=migrate_engine,
                                                    metadata=migrate_metadata)


# Existing classes and tables to be used in relations
projects = Table('projects', migrate_metadata, autoload=True)
taggables = Table('taggables', migrate_metadata, autoload=True)
annotables = Table('annotables', migrate_metadata, autoload=True)

# New classes and tables
class AssetContainer(DeclarativeBase):
    """Base class for object containers"""
    __tablename__ = 'asset_containers'
        
    id = Column(Integer, primary_key=True)
    proj_id = Column(Unicode(10))
    type = Column(Unicode(20))
    __mapper_args__ = {'polymorphic_on': type}


class Scene(DeclarativeBase):
    """
    The scene container.
    
    This represents a "film scene" that acts as a container for Shot objects.
    """
    __tablename__ = "scenes"
    __table_args__ = (UniqueConstraint('proj_id', 'name'),
                      ForeignKeyConstraint(['taggable_id', 'proj_id'],
                                    ['taggables.id', 'taggables.proj_id']),
                      ForeignKeyConstraint(['annotable_id', 'proj_id'],
                                    ['annotables.id', 'annotables.proj_id']),
                      {})
    
    # Columns
    id = Column(Integer, primary_key=True)
    proj_id = Column(Unicode(10), ForeignKey('projects.id'))
    name = Column(Unicode(15))
    description = Column(UnicodeText)
    created = Column(DateTime, default=datetime.now)
    annotable_id = Column(Integer)
    taggable_id = Column(Integer)


class Shot(AssetContainer):
    """
    The shot container.

    This represents a "film shot" that acts as a container for Asset objects.
    """
    __tablename__ = "shots"
    __table_args__ = (UniqueConstraint('proj_id', 'parent_id', 'name'),
                      ForeignKeyConstraint(['id', 'proj_id'],
                          ['asset_containers.id', 'asset_containers.proj_id']),
                      ForeignKeyConstraint(['parent_id', 'proj_id'],
                          ['scenes.id', 'scenes.proj_id']),
                      ForeignKeyConstraint(['taggable_id', 'proj_id'],
                                    ['taggables.id', 'taggables.proj_id']),
                      ForeignKeyConstraint(['annotable_id', 'proj_id'],
                                    ['annotables.id', 'annotables.proj_id']),
                      {})
    __mapper_args__ = {'polymorphic_identity': 'shot'}
    
    # Columns
    id = Column(Integer, primary_key=True)
    proj_id = Column(Unicode(10))
    parent_id = Column(Integer)
    name = Column(Unicode(15))
    created = Column(DateTime, default=datetime.now)
    description = Column(UnicodeText)
    location = Column(Unicode(255))
    action = Column(UnicodeText)
    frames = Column(Integer)
    handle_in = Column(Integer)
    handle_out = Column(Integer)
    taggable_id = Column(Integer)
    annotable_id = Column(Integer)


class LibraryGroup(AssetContainer):
    """Library group"""
    __tablename__ = "library_groups"
    __table_args__ = (UniqueConstraint('proj_id', 'parent_id', 'name'),
                      ForeignKeyConstraint(['id', 'proj_id'],
                          ['asset_containers.id', 'asset_containers.proj_id']),
                      ForeignKeyConstraint(['parent_id'],
                          ['library_groups.id']),
                      ForeignKeyConstraint(['taggable_id', 'proj_id'],
                                    ['taggables.id', 'taggables.proj_id']),
                      ForeignKeyConstraint(['annotable_id', 'proj_id'],
                                    ['annotables.id', 'annotables.proj_id']),
                      {})
    __mapper_args__ = {'polymorphic_identity': 'library_group'}
    
    # Columns
    id = Column(Integer, primary_key=True)
    proj_id = Column(Unicode(10))
    parent_id = Column(Integer)
    name = Column(Unicode(40))
    description = Column(UnicodeText)
    taggable_id = Column(Integer)
    annotable_id = Column(Integer)


def upgrade():
    # Upgrade operations go here. Don't create your own engine; use the engine
    # named 'migrate_engine' imported from migrate.
    AssetContainer.__table__.create()
    Scene.__table__.create()
    Shot.__table__.create()
    LibraryGroup.__table__.create()
    
def downgrade():
    # Operations to reverse the above upgrade go here.
    AssetContainer.__table__.drop()
    Scene.__table__.drop()
    Shot.__table__.drop()
    LibraryGroup.__table__.create()

