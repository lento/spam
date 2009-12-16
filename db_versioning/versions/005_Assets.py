from datetime import datetime
from sqlalchemy import Table, Column, MetaData, and_
from sqlalchemy import UniqueConstraint, ForeignKeyConstraint, ForeignKey
from sqlalchemy.types import Unicode, UnicodeText, DateTime, Integer, Boolean
from sqlalchemy.types import String
from sqlalchemy.orm import relation, backref
from migrate import *
from sqlalchemy.ext.declarative import declarative_base

migrate_metadata = MetaData()
DeclarativeBase = declarative_base(bind=migrate_engine,
                                                    metadata=migrate_metadata)


# Existing classes and tables to be used in relations
auth_users = Table('auth_users', migrate_metadata, autoload=True)
asset_containers = Table('asset_containers', migrate_metadata, autoload=True)

# New classes and tables
class Asset(DeclarativeBase):
    """Asset"""
    __tablename__ = "assets"
    __table_args__ = (UniqueConstraint('category_id', 'parent_id', 'name'),
                      ForeignKeyConstraint(['parent_id', 'proj_id'],
                          ['asset_containers.id', 'asset_containers.proj_id']),
                      {})
    
    # Columns
    id = Column(Integer, autoincrement=True, primary_key=True)
    proj_id = Column(Unicode(10))
    name = Column(Unicode(50))
    parent_id = Column(Integer)
    category_id = Column(Integer, ForeignKey('categories.id'))
    user_id = Column(Integer, ForeignKey('auth_users.user_id'))
    checkedout = Column(Boolean, default=False)
    submitter_id = Column(Integer, ForeignKey('auth_users.user_id'))
    submitted = Column(Boolean, default=False)
    submitted_date = Column(DateTime)
    approver_id = Column(Integer, ForeignKey('auth_users.user_id'))
    approved = Column(Boolean, default=False)
    approved_date = Column(DateTime)


class AssetVersion(DeclarativeBase):
    """Asset version"""
    __tablename__ = "asset_versions"
    
    # Columns
    id = Column(Integer, primary_key=True)
    proj_id = Column(Unicode(10))
    asset_id = Column(Integer, ForeignKey('assets.id'))
    ver = Column(Integer)
    created = Column(DateTime, default=datetime.now)
    repoid = Column(String(50))
    #has_preview = Column(Boolean)
    #preview_ext = Column(String(10))
    user_id = Column(Integer, ForeignKey('auth_users.user_id'))
    #note_id = Column(None, ForeignKey('notes_associations.assoc_id'))


class Category(DeclarativeBase):
    """Asset category"""
    __tablename__ = "categories"
    
    # Columns
    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(Unicode(30), unique=True)
    ordering = Column(Integer)
    naming_convention = Column(Unicode(255))


class Supervisor(DeclarativeBase):
    """Category supervisor"""
    __tablename__ = "supervisors"
    
    # Columns
    id = Column(Integer, autoincrement=True, primary_key=True)
    proj_id = Column(Unicode(10))
    category_id = Column(Integer)
    user_id = Column(Integer)


class Artist(DeclarativeBase):
    """Category artist"""
    __tablename__ = "artists"
    
    # Columns
    id = Column(Integer, autoincrement=True, primary_key=True)
    proj_id = Column(Unicode(10))
    category_id = Column(Integer)
    user_id = Column(Integer)


def upgrade():
    # Upgrade operations go here. Don't create your own engine; use the engine
    # named 'migrate_engine' imported from migrate.
    Asset.__table__.create()
    AssetVersion.__table__.create()
    Category.__table__.create()
    Supervisor.__table__.create()
    Artist.__table__.create()

def downgrade():
    # Operations to reverse the above upgrade go here.
    Asset.__table__.drop()
    AssetVersion.__table__.drop()
    Category.__table__.drop()
    Supervisor.__table__.drop()
    Artist.__table__.drop()

