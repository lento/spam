from datetime import datetime
from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from migrate import *

metadata = MetaData()
DeclarativeBase = declarative_base(metadata=metadata)

# New classes and tables
projects_admins_table = Table('__projects_admins', metadata,
    Column('project_id', Unicode(10), ForeignKey('projects.id',
                                    onupdate="CASCADE", ondelete="CASCADE")),
    Column('user_id', Unicode(40), ForeignKey('users.user_id',
                                    onupdate="CASCADE", ondelete="CASCADE"))
)

# Project
class Project(DeclarativeBase):
    __tablename__ = 'projects'
    
    id = Column(Unicode(10), primary_key=True)
    name = Column(Unicode(40))
    description = Column(UnicodeText())
    modified = Column(DateTime, default=datetime.now)
    archived = Column(Boolean, default=False)


# Containers
class AssetContainer(DeclarativeBase):
    """Base class for object containers"""
    __tablename__ = 'asset_containers'
        
    # Columns
    id = Column(String(40), primary_key=True)
    association_type = Column(Unicode(50))


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


class Shot(DeclarativeBase):
    """
    The shot container.

    This represents a "film shot" that acts as a container for Asset objects.
    """
    __tablename__ = "shots"
    __table_args__ = (UniqueConstraint('parent_id', 'name'),
                      ForeignKeyConstraint(['id'], ['asset_containers.id']),
                      ForeignKeyConstraint(['id'], ['taggables.id']),
                      ForeignKeyConstraint(['id'], ['annotables.id']),
                      {})
    
    # Columns
    id = Column(String(40), primary_key=True)
    parent_id = Column(String(40), ForeignKey('scenes.id'))
    name = Column(Unicode(15))
    description = Column(UnicodeText)
    location = Column(Unicode(255))
    action = Column(UnicodeText)
    frames = Column(Integer)
    handle_in = Column(Integer)
    handle_out = Column(Integer)
    

class Libgroup(DeclarativeBase):
    """Library group"""
    __tablename__ = "libgroups"
    __table_args__ = (UniqueConstraint('parent_id', 'name'),
                      ForeignKeyConstraint(['id'], ['asset_containers.id']),
                      ForeignKeyConstraint(['id'], ['taggables.id']),
                      ForeignKeyConstraint(['id'], ['annotables.id']),
                      {})
    
    # Columns
    id = Column(String(40), primary_key=True)
    proj_id = Column(Unicode(10), ForeignKey('projects.id'))
    parent_id = Column(String(40), ForeignKey('libgroups.id'))
    name = Column(Unicode(40))
    description = Column(UnicodeText)
    

# Categories
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


# Assets
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
    submitted_date =  Column(DateTime)
    approved = Column(Boolean, default=False)
    approver_id = Column(Integer, ForeignKey('users.user_id'))
    approved_date =  Column(DateTime)


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
    user_id = Column(Integer, ForeignKey('users.user_id'))


def upgrade(migrate_engine):
    """operations to upgrade the db"""
    metadata.bind = migrate_engine

    # Existing classes and tables to be used in relations
    users = Table('users', metadata, autoload=True)
    taggables = Table('taggables', metadata, autoload=True)
    annotables = Table('annotables', metadata, autoload=True)

    Project.__table__.create()
    projects_admins_table.create()

    AssetContainer.__table__.create()
    Scene.__table__.create()
    Shot.__table__.create()
    Libgroup.__table__.create()

    Category.__table__.create()
    Supervisor.__table__.create()
    Artist.__table__.create()
    Asset.__table__.create()
    AssetVersion.__table__.create()

def downgrade(migrate_engine):
    """operations to reverse the above upgrade"""
    metadata.bind = migrate_engine

    # Existing classes and tables to be used in relations
    users = Table('users', metadata, autoload=True)
    taggables = Table('taggables', metadata, autoload=True)
    annotables = Table('annotables', metadata, autoload=True)

    projects_admins_table.drop()
    Project.__table__.drop()

    AssetContainer.__table__.drop()
    Scene.__table__.drop()
    Shot.__table__.drop()
    Libgroup.__table__.drop()

    Category.__table__.drop()
    Supervisor.__table__.drop()
    Artist.__table__.drop()
    AssetVersion.__table__.drop()
    Asset.__table__.drop()

