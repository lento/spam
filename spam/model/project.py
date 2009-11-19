"""
Project data model.

This is where the model for project data is defined.
"""
from datetime import datetime

from sqlalchemy import Table, ForeignKey, Column, UniqueConstraint
from sqlalchemy import ForeignKeyConstraint, and_
from sqlalchemy.types import Unicode, UnicodeText, Integer, DateTime
from sqlalchemy.orm import relation, synonym, backref

from spam.model import DeclarativeBase, metadata, DBSession

__all__ = ['Project']


#{ Association tables


# Association table for the many-to-many relationship projects-users.
project_user_table = Table('__project_user', metadata,
    Column('project_id', Unicode(10), ForeignKey('projects.id',
        onupdate="CASCADE", ondelete="CASCADE")),
    Column('user_id', Integer, ForeignKey('auth_users.user_id',
        onupdate="CASCADE", ondelete="CASCADE"))
)

# Association table for the many-to-many relationship projects-admins.
project_admin_table = Table('__project_admin', metadata,
    Column('project_id', Unicode(10), ForeignKey('projects.id',
        onupdate="CASCADE", ondelete="CASCADE")),
    Column('user_id', Integer, ForeignKey('auth_users.user_id',
        onupdate="CASCADE", ondelete="CASCADE"))
)


#{ The Common model itself


class Project(DeclarativeBase):
    """
    Project definition.
    
    """
    
    __tablename__ = 'projects'
    
    #{ Columns
    id = Column(Unicode(10), primary_key=True)
    name = Column(Unicode(40))
    description = Column(Unicode)
    created = Column(DateTime, default=datetime.now)
    modified = Column(DateTime, default=datetime.now)
    
    #{ Relations
    users = relation('User', secondary=project_user_table, backref='projects')
    admins = relation('User', secondary=project_admin_table,
                                                    backref='admin_projects')
    
    #{ Special methods
    def __init__(self, id, name=None, description=None):
        self.id = id
        self.name = name
        self.description = description

    def __repr__(self):
        return '<Project: %s "%s">' % (self.id, self.name)
    
    def __json__(self):
        return dict(id=self.id,
                    name=self.name,
                    description=self.description,
                    created=self.created.strftime('%Y/%m/%d %H:%M'),
                    modified=self.modified.strftime('%Y/%m/%d %H:%M'),
                   )
    #}


# Containers
class AssetContainer(DeclarativeBase):
    """Base class for object containers"""
    __tablename__ = 'asset_containers'
        
    id = Column(Integer, primary_key=True)
    proj_id = Column(Unicode(10))
    type = Column(Unicode(20))
    __mapper_args__ = {'polymorphic_on': type}

    def __repr__(self):
        return '<AssetContainer: (%s) %d>' % (self.proj_id, self.id)


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

    project = relation('Project', primaryjoin='Scene.proj_id==Project.id',
                       foreign_keys=[proj_id], viewonly=True,
                       backref=backref('scenes', viewonly=True, order_by=name)
                      )
    
    def __init__(self, proj, name, description=None):
        self.proj_id = proj
        self.name = name
        self.description = description

    def __repr__(self):
        return '<Scene: (%s) "%s">' % (self.proj_id, self.name)

    def __json__(self):
        return dict(id=self.id,
                    proj_id=self.proj_id,
                    name=self.name,
                    description=self.description,
                    created=self.created.strftime('%Y/%m/%d %H:%M'),
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
    
    parent = relation(Scene,
                        backref=backref('shots', order_by=name, lazy=False))
    
    def __init__(self, proj_id, name, group=None, description=None,
                            location=None, frames=0, handle_in=0, handle_out=0,
                            action='', parent=None):
        self.proj_id = proj_id
        self.name = name
        #self.group = group
        self.description = description
        self.location = location
        self.frames = frames
        self.handle_in = handle_in
        self.handle_out = handle_out
        self.action = action
        self.parent = parent

    def __repr__(self):
        return '<Shot: (%s) "%s">' % (self.proj_id, self.name)

    def __json__(self):
        return dict(id=self.id,
                    proj_id=self.proj_id,
                    parent_id=self.parent_id,
                    name=self.name,
                    description=self.description,
                    created=self.created.strftime('%Y/%m/%d %H:%M'),
                    location=self.location,
                    action=self.action,
                    frames=self.frames,
                    handle_in=self.handle_in,
                    handle_out=self.handel_out,
                   )
                    

class LibraryGroup(AssetContainer):
    """Library group"""
    __tablename__ = "library_groups"
    __table_args__ = (UniqueConstraint('proj_id', 'parent_id', 'name'),
                      ForeignKeyConstraint(['id', 'proj_id'],
                          ['asset_containers.id', 'asset_containers.proj_id']),
                      ForeignKeyConstraint(['parent_id'],
                          ['library_groups.id']),
                      {})
    __mapper_args__ = {'polymorphic_identity': 'library_group'}
    
    id = Column(Integer, primary_key=True)
    proj_id = Column(Unicode(10))
    parent_id = Column(Integer)
    name = Column(Unicode(40))
    description = Column(UnicodeText)
    #note_id = Column(None, ForeignKey('notes_associations.assoc_id'))
    
    project = relation('Project',
                primaryjoin='AssetContainer.proj_id==Project.id',
                foreign_keys=[AssetContainer.proj_id],
                viewonly=True,
                backref=backref('libgroups',
                                primaryjoin=
                                    'and_(Project.id==LibraryGroup.proj_id, '
                                    'LibraryGroup.parent_id==None)',
                                viewonly=True, order_by=name
                               )
              )
    
    subgroups = relation('LibraryGroup',
                         primaryjoin=and_(parent_id==id, proj_id==proj_id),
                         foreign_keys=[parent_id, proj_id],
                         lazy=False, join_depth=5,
                         # this backref doesn't work...
                         #backref=backref('parent',
                         #                primaryjoin=and_(id==parent_id, proj_id==proj_id),
                         #                foreign_keys=[id, proj_id],
                         #                remote_side=[parent_id, proj_id]
                         #               )
                        )
    
    parent = relation('LibraryGroup',
                      primaryjoin=and_(id==parent_id, proj_id==proj_id),
                      foreign_keys=[id, proj_id], uselist=False,
                     )
    
    #supervisors = relation('ProjectUser', secondary=supervisors_libgroup_table,
    #                        order_by='ProjectUser.user_name',
    #                        backref=backref('supervised_libgroups'))
    
    def __init__(self, proj, name, parent=None, description=None):
        self.proj_id = proj
        self.name = name
        self.parent = parent
        self.description = description

    def __repr__(self):
        return '<LibraryGroup: (%s) "%s">' % (self.proj_id, self.name)

    def __json__(self):
        return dict(id=self.id,
                    proj_id=self.proj_id,
                    parent_id=self.parent_id,
                    name=self.name,
                    description=self.description,
                    #created=self.created.strftime('%Y/%m/%d %H:%M'),
                   )


