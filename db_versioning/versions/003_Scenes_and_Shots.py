from datetime import datetime
from sqlalchemy import Table, Column
from sqlalchemy import UniqueConstraint, ForeignKeyConstraint, ForeignKey
from sqlalchemy.types import Unicode, UnicodeText, DateTime, Integer
from sqlalchemy.orm import relation, backref
from migrate import *
from sqlalchemy.ext.declarative import declarative_base

DeclarativeBase = declarative_base(bind=migrate_engine)
metadata = DeclarativeBase.metadata


# Existing classes and tables to be used in relations
projects = Table('projects', metadata, autoload=True)

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
    
    This models a "film scene" that acts as a container for Shot objects.
    """
    __tablename__ = "scenes"
    __table_args__ = (UniqueConstraint('proj_id', 'name'),
                      {})
    
    id = Column(Integer, primary_key=True)
    proj_id = Column(Unicode(10))
    name = Column(Unicode(15))
    description = Column(UnicodeText)
    #group = Column(Unicode(40))
    created = Column(DateTime, default=datetime.now)

    project = relation('Project',
                primaryjoin='Scene.proj_id==Project.id',
                foreign_keys=[proj_id],
                viewonly=True,
                backref=backref('scenes',
                    primaryjoin='Project.id==Scene.proj_id',
                    foreign_keys=[projects.c.id], viewonly=True, uselist=True,
                    order_by=name)
                )


class Shot(AssetContainer):
    """
    The shot container.

    This models a "film shot" that acts as a container for Asset objects.
    """
    __tablename__ = "shots"
    __table_args__ = (UniqueConstraint('proj_id', 'parent_id', 'name'),
                      ForeignKeyConstraint(['id', 'proj_id'],
                          ['asset_containers.id', 'asset_containers.proj_id']),
                      ForeignKeyConstraint(['parent_id', 'proj_id'],
                          ['scenes.id', 'scenes.proj_id']),
                      {})
    __mapper_args__ = {'polymorphic_identity': 'shot'}
    
    id = Column(Integer, primary_key=True)
    proj_id = Column(Unicode(10))
    parent_id = Column(Integer)
    name = Column(Unicode(15))
    description = Column(UnicodeText)
    #_group = Column(Unicode(40))
    location = Column(Unicode(255))
    action = Column(UnicodeText)
    #elements = Column(UnicodeText)
    #characters = Column(UnicodeText)
    #props = Column(UnicodeText)
    created = Column(DateTime, default=datetime.now)
    frames = Column(Integer)
    handle_in = Column(Integer)
    handle_out = Column(Integer)
    #assoc_id = Column(None, ForeignKey('notes_associations.assoc_id'))


def upgrade():
    # Upgrade operations go here. Don't create your own engine; use the engine
    # named 'migrate_engine' imported from migrate.
    AssetContainer.__table__.create()
    Scene.__table__.create()
    Shot.__table__.create()
    
def downgrade():
    # Operations to reverse the above upgrade go here.
    AssetContainer.__table__.drop()
    Scene.__table__.drop()
    Shot.__table__.drop()

