from datetime import datetime
from sqlalchemy import Table, Column, MetaData, and_, DDL
from sqlalchemy import UniqueConstraint, ForeignKeyConstraint, ForeignKey
from sqlalchemy.types import Unicode, UnicodeText, DateTime, Integer, Boolean
from sqlalchemy.types import String
from sqlalchemy.orm import relation, backref
from migrate import *
from sqlalchemy.ext.declarative import declarative_base

metadata = MetaData()
DeclarativeBase = declarative_base(bind=migrate_engine, metadata=metadata)

# Existing classes and tables to be used in relations
projects = Table('projects', metadata, autoload=True)
users = Table('users', metadata, autoload=True)
asset_containers = Table('asset_containers', metadata, autoload=True)
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
class Category(DeclarativeBase):
    """Asset category"""
    __tablename__ = "categories"
    
    # Columns
    id = Column(Unicode(40), primary_key=True)
    ordering = Column(Integer)
    naming_convention = Column(Unicode(255))


class Supervisor(DeclarativeBase):
    """Category supervisor"""
    __tablename__ = "supervisors"
    __table_args__ = (UniqueConstraint('proj_id', 'category_id', 'user_id'),
                      {})
    
    # Columns
    id = Column(String(40), primary_key=True)
    proj_id = Column(Unicode(10), ForeignKey('projects.id'))
    category_id = Column(Unicode(40), ForeignKey('categories.id'))
    user_id = Column(Unicode(40), ForeignKey('users.user_id'))


class Artist(DeclarativeBase):
    """Category artist"""
    __tablename__ = "artists"
    __table_args__ = (UniqueConstraint('proj_id', 'category_id', 'user_id'),
                      {})
    
    # Columns
    id = Column(String(40), primary_key=True)
    proj_id = Column(Unicode(10), ForeignKey('projects.id'))
    category_id = Column(Unicode(40), ForeignKey('categories.id'))
    user_id = Column(Unicode(40), ForeignKey('users.user_id'))


class Asset(DeclarativeBase):
    """Asset"""
    __tablename__ = "assets"
    __table_args__ = (UniqueConstraint('parent_id', 'category_id', 'name'),
                      ForeignKeyConstraint(['id'], ['taggables.id']),
                      {})
    
    # Columns
    id = Column(String(40), primary_key=True)
    name = Column(Unicode(50))
    parent_id = Column(String(40), ForeignKey('asset_containers.id'))
    category_id = Column(Integer, ForeignKey('categories.id'))
    checkedout = Column(Boolean, default=False)
    owner_id = Column(Integer, ForeignKey('users.user_id'))
    submitted = Column(Boolean, default=False)
    submitter_id = Column(Integer, ForeignKey('users.user_id'))
    submitted_date =  Column(DateTime, default=datetime.now)
    approved = Column(Boolean, default=False)
    approver_id = Column(Integer, ForeignKey('users.user_id'))
    approved_date =  Column(DateTime, default=datetime.now)

DDL(taggable_delete_trigger).execute_at('after-create', Asset.__table__)


class AssetVersion(DeclarativeBase):
    """Asset version"""
    __tablename__ = "asset_versions"
    __table_args__ = (UniqueConstraint('asset_id', 'ver'),
                      ForeignKeyConstraint(['id'], ['annotables.id']),
                      {})
    
    # Columns
    id = Column(String(40), primary_key=True)
    asset_id = Column(String(40), ForeignKey('assets.id'))
    ver = Column(Integer)
    repoid = Column(String(50))
    #has_preview = Column(Boolean)
    #preview_ext = Column(String(10))
    user_id = Column(Integer, ForeignKey('users.user_id'))

DDL(annotable_delete_trigger).execute_at('after-create', AssetVersion.__table__)

def upgrade():
    # Upgrade operations go here. Don't create your own engine; use the engine
    # named 'migrate_engine' imported from migrate.
    Category.__table__.create()
    Supervisor.__table__.create()
    Artist.__table__.create()
    Asset.__table__.create()
    AssetVersion.__table__.create()

def downgrade():
    # Operations to reverse the above upgrade go here.
    Category.__table__.drop()
    Supervisor.__table__.drop()
    Artist.__table__.drop()
    AssetVersion.__table__.drop()
    Asset.__table__.drop()

