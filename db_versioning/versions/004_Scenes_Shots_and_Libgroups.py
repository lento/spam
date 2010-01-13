from datetime import datetime
from sqlalchemy import Table, Column, MetaData, DDL
from sqlalchemy import UniqueConstraint, ForeignKeyConstraint, ForeignKey
from sqlalchemy.types import Unicode, UnicodeText, DateTime, Integer, String
from sqlalchemy.orm import relation, backref
from migrate import *
from sqlalchemy.ext.declarative import declarative_base

metadata = MetaData()
DeclarativeBase = declarative_base(bind=migrate_engine, metadata=metadata)


# Existing classes and tables to be used in relations
projects = Table('projects', metadata, autoload=True)
taggables = Table('taggables', metadata, autoload=True)
annotables = Table('annotables', metadata, autoload=True)

taggable_delete_trigger = (
    'CREATE TRIGGER delete_orphaned_%(table)s_taggable DELETE ON %(table)s '
    'BEGIN '
        'DELETE FROM taggables WHERE id=old.id; '
    'END;')

annotable_delete_trigger = (
    'CREATE TRIGGER delete_orphaned_%(table)s_annotable DELETE ON %(table)s '
    'BEGIN '
        'DELETE FROM annotables WHERE id=old.id; '
    'END;')


# New classes and tables
class AssetContainer(DeclarativeBase):
    """Base class for object containers"""
    __tablename__ = 'asset_containers'
        
    # Columns
    id = Column(String(40), primary_key=True)
    discriminator = Column('type', Unicode(20))
    __mapper_args__ = {'polymorphic_on': discriminator}

class Scene(DeclarativeBase):
    """
    The scene container.
    
    This represents a "film scene" that acts as a container for Shot objects.
    """
    __tablename__ = "scenes"
    __table_args__ = (UniqueConstraint('proj_id', 'name'),
                      ForeignKeyConstraint(['id'], ['taggables.id']),
                      ForeignKeyConstraint(['id'], ['annotables.id']),
                      {})
    
    # Columns
    id = Column(String(40), primary_key=True)
    proj_id = Column(Unicode(10), ForeignKey('projects.id'))
    name = Column(Unicode(15))
    description = Column(UnicodeText)

DDL(taggable_delete_trigger).execute_at('after-create', Scene.__table__)
DDL(annotable_delete_trigger).execute_at('after-create', Scene.__table__)


class Shot(AssetContainer):
    """
    The shot container.

    This represents a "film shot" that acts as a container for Asset objects.
    """
    __tablename__ = "shots"
    __table_args__ = (UniqueConstraint('parent_id', 'name'),
                      ForeignKeyConstraint(['id'], ['taggables.id']),
                      ForeignKeyConstraint(['id'], ['annotables.id']),
                      {})
    __mapper_args__ = {'polymorphic_identity': 'shot'}
    
    # Columns
    id = Column(String(40), ForeignKey('asset_containers.id'), primary_key=True)
    parent_id = Column(String(40), ForeignKey('scenes.id'))
    name = Column(Unicode(15))
    description = Column(UnicodeText)
    location = Column(Unicode(255))
    action = Column(UnicodeText)
    frames = Column(Integer)
    handle_in = Column(Integer)
    handle_out = Column(Integer)
    taggable_id = Column(Integer)
    annotable_id = Column(Integer)

DDL(taggable_delete_trigger).execute_at('after-create', Shot.__table__)
DDL(annotable_delete_trigger).execute_at('after-create', Shot.__table__)


class LibraryGroup(AssetContainer):
    """Library group"""
    __tablename__ = "library_groups"
    __table_args__ = (UniqueConstraint('parent_id', 'name'),
                      ForeignKeyConstraint(['id'], ['taggables.id']),
                      ForeignKeyConstraint(['id'], ['annotables.id']),
                      {})
    __mapper_args__ = {'polymorphic_identity': 'library_group'}
    
    # Columns
    id = Column(String(40), ForeignKey('asset_containers.id'), primary_key=True)
    proj_id = Column(Unicode(10), ForeignKey('projects.id'))
    parent_id = Column(String(40), ForeignKey('library_groups.id'))
    name = Column(Unicode(40))
    description = Column(UnicodeText)

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

DDL(taggable_delete_trigger).execute_at('after-create', LibraryGroup.__table__)
DDL(annotable_delete_trigger).execute_at('after-create', LibraryGroup.__table__)

