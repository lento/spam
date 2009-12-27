"""
Project data model.

This is where the model for project data is defined.
"""
import os.path
from datetime import datetime

from sqlalchemy import Table, ForeignKey, Column, UniqueConstraint
from sqlalchemy import ForeignKeyConstraint, and_, desc
from sqlalchemy.types import Unicode, UnicodeText, Integer, DateTime, Boolean
from sqlalchemy.types import String
from sqlalchemy.orm import relation, synonym, backref

from tg import app_globals as G
from spam.model import DeclarativeBase, metadata, mapped_list
from spam.model import migraterepo_get_version, db_get_version
from spam.model import db_upgrade, db_downgrade
from spam.model.auth import User

import logging
log = logging.getLogger(__name__)

__all__ = ['Project']

############################################################
# Association tables
############################################################

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


############################################################
# Tags
############################################################
class Taggable(DeclarativeBase):
    __tablename__ = 'taggables'
    
    # Columns
    id = Column(Integer, autoincrement=True, primary_key=True)
    proj_id = Column(Unicode(10))
    association_type = Column(Unicode(50))
    
    # Properties
    @property
    def tagged(self):
        return getattr(self, 'tagged_%s' % self.association_type)
    
    # Special methods
    def __init__(self, proj, association_type):
        self.proj_id = proj
        self.association_type = association_type

    def __repr__(self):
        return '<Taggable: (%s.%s) %d>' % (self.proj_id, self.association_type,
                                                                        self.id)


class Tag(DeclarativeBase):
    __tablename__ = 'tags'
    __table_args__ = (ForeignKeyConstraint(['taggable_id', 'proj_id'],
                                        ['taggables.id', 'taggables.proj_id']),
                      {})
    
    # Columns
    id = Column(Integer, autoincrement=True, primary_key=True)
    proj_id = Column(Unicode(10))
    taggable_id = Column(Integer)
    name = Column(UnicodeText, unique=True)
    created = Column(DateTime, default=datetime.now)
    
    # Relations
    taggable = relation(Taggable, backref='tags')
    
    # Properties
    @property
    def tagged(self):
        return self.taggable.tagged
    
    # Special methods
    def __init__(self, proj, name):
        self.proj_id = proj
        self.name = name

    def __repr__(self):
        return '<Tag: %s>' % self.name

    def __json__(self):
        return {'id': self.id,
                'created': self.created,
                'name': self.name,
               }


############################################################
# Notes
############################################################
class Annotable(DeclarativeBase):
    __tablename__ = 'annotables'
    
    # Columns
    id = Column(Integer, autoincrement=True, primary_key=True)
    proj_id = Column(Unicode(10))
    association_type = Column(Unicode(50))
    
    # Properties
    @property
    def annotated(self):
        return getattr(self, 'annotated_%s' % self.association_type)
    
    # Special methods
    def __init__(self, proj, association_type):
        self.proj_id = proj
        self.association_type = association_type

    def __repr__(self):
        return '<Annotable: (%s.%s) %d>' % (self.proj_id, self.association_type,
                                                                        self.id)


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

    user = relation('User', primaryjoin=user_id==User.user_id,
                            foreign_keys=[user_id],
                            backref=backref('notes', order_by=desc('created')))
    
    # Relations
    annotable = relation(Annotable, backref='notes')
    
    # Properties
    @property
    def annotated(self):
        return self.annotable.annotated
    
    @property
    def strftime(self):
        return self.created.strftime('%d/%m/%Y %H:%M')
    
    @property
    def summary(self):
        characters = 75
        summary = self.text[0:characters]
        if len(self.text) > characters:
            summary = '%s[...]' % summary
        return summary
    
    @property
    def lines(self):
        return [l for l in self.text.split('\n')]
    
    # Special methods
    def __init__(self, proj, user, text):
        self.proj_id = proj
        self.user = user
        self.text = text

    def __repr__(self):
        return '<Note: by %s at %s "%s">' % (self.user.user_name,
                                                self.strftime,
                                                self.summary)

    def __json__(self):
        return {'id': self.id,
                #'owner_id': self.owner_id,
                'user': self.user,
                'created': self.created,
                'text': self.text,
                'summary': self.summary,
                'lines': self.lines,
                'strftime': self.strftime,
               }


############################################################
# Project
############################################################
class Project(DeclarativeBase):
    """Project definition."""
    __tablename__ = 'projects'
    
    # Columns
    id = Column(Unicode(10), primary_key=True)
    name = Column(Unicode(40))
    description = Column(Unicode)
    created = Column(DateTime, default=datetime.now)
    modified = Column(DateTime, default=datetime.now)
    archived = Column(Boolean, default=False)
    
    # Relations
    admins = relation('User', secondary=project_admin_table,
                                                    backref='projects_as_admin')
    
    # Properties
    @property
    def users(self):
        return (set([s.user for s in self.supervisors]) |
                set([a.user for a in self.artists]))
    
    @property
    def schema_is_uptodate(self):
        proj_version = db_get_version(self.id)
        repo_version = migraterepo_get_version()
        return proj_version==repo_version
    
    @property
    def schema_version(self):
        return db_get_version(self.id)
    
    # Methods
    def touch(self):
        self.modified = datetime.now()
    
    def schema_upgrade(self, version=None):
        db_upgrade(self.id, version)
    
    def schema_downgrade(self, version):
        db_downgrade(self.id, version)
    
    # Special methods
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
                    archived=self.archived,
                    schema_is_uptodate=self.schema_is_uptodate,
                   )


############################################################
# Containers
############################################################
class AssetContainer(DeclarativeBase):
    """Base class for object containers"""
    __tablename__ = 'asset_containers'
        
    # Columns
    id = Column(Integer, primary_key=True)
    proj_id = Column(Unicode(10))
    discriminator = Column('type', Unicode(20))
    __mapper_args__ = {'polymorphic_on': discriminator}

    # Special methods
    def __repr__(self):
        return '<AssetContainer: (%s) %d>' % (self.proj_id, self.id)


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
    proj_id = Column(Unicode(10), ForeignKey(Project.id))
    name = Column(Unicode(15))
    description = Column(UnicodeText)
    created = Column(DateTime, default=datetime.now)
    annotable_id = Column(Integer)
    taggable_id = Column(Integer)

    # Relations
    project = relation('Project', viewonly=True,
                       backref=backref('scenes', viewonly=True, order_by=name)
                      )
    
    taggable = relation(Taggable, backref='tagged_scenes')
    
    annotable = relation(Annotable, backref='annotated_scenes')
    
    # Properties
    @property
    def path(self):
        return os.path.join(G.SCENES, self.name)
    
    @property
    def thumbnail(self):
        return os.path.join(G.PREVIEWS, self.path, 'thumb.png')
    
    @property
    def tags(self):
        return self.taggable.tags
    
    @property
    def notes(self):
        return self.annotable.notes
    
    # Special methods
    def __init__(self, proj, name, description=None):
        self.proj_id = proj
        self.name = name
        self.description = description
        self.taggable = Taggable(self.proj_id, 'scenes')
        self.annotable = Annotable(self.proj_id, 'scenes')

    def __repr__(self):
        return '<Scene: (%s) "%s">' % (self.proj_id, self.name)

    def __json__(self):
        return dict(id=self.id,
                    proj_id=self.proj_id,
                    name=self.name,
                    description=self.description,
                    created=self.created.strftime('%Y/%m/%d %H:%M'),
                    thumbnail=self.thumbnail,
                   )

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
    
    # Relations
    project = relation('Project', primaryjoin=proj_id==Project.id,
                       foreign_keys=[proj_id], viewonly=True,
                      )
    
    parent = relation(Scene,
                        backref=backref('shots', order_by=name, lazy=False))
    
    taggable = relation(Taggable, backref='tagged_shots')
    
    annotable = relation(Annotable, backref='annotated_shots')
    
    # Properties
    @property
    def path(self):
        return os.path.join(self.parent.path, self.name)
    
    @property
    def parent_name(self):
        return self.parent.name
    
    @property
    def tags(self):
        return self.taggable.tags
    
    @property
    def notes(self):
        return self.annotable.notes
    
    # Special methods
    def __init__(self, proj_id, name, parent=None,
                       description=None, action=None, location=None,
                       frames=0, handle_in=0, handle_out=0,
                ):
        self.proj_id = proj_id
        self.name = name
        self.description = description
        self.location = location
        self.frames = frames
        self.handle_in = handle_in
        self.handle_out = handle_out
        self.action = action
        self.parent = parent
        self.taggable = Taggable(self.proj_id, 'shots')
        self.annotable = Annotable(self.proj_id, 'shots')

    def __repr__(self):
        return '<Shot: (%s) "%s">' % (self.proj_id, self.name)

    def __json__(self):
        return dict(id=self.id,
                    proj_id=self.proj_id,
                    parent_id=self.parent_id,
                    parent_name=self.parent_name,
                    name=self.name,
                    description=self.description,
                    created=self.created.strftime('%Y/%m/%d %H:%M'),
                    location=self.location,
                    action=self.action,
                    frames=self.frames,
                    handle_in=self.handle_in,
                    handle_out=self.handle_out,
                   )
                    

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
    
    # Relations
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
                      foreign_keys=[id, proj_id], uselist=False, viewonly=True,
                     )
    
    taggable = relation(Taggable, backref='tagged_libgroups')
    
    annotable = relation(Annotable, backref='annotated_libgroups')
    
    # Properties
    @property
    def path(self):
        if self.parent_id:
            path = self.parent.path
        else:
            path = G.LIBRARY
        path = os.path.join(path, self.name)
        return path
    
    @property
    def tags(self):
        return self.taggable.tags
    
    @property
    def notes(self):
        return self.annotable.notes
    
    # Special methods
    def __init__(self, proj, name, parent=None, description=None):
        self.proj_id = proj
        self.name = name
        if parent: self.parent_id = parent.id
        self.description = description
        self.taggable = Taggable(self.proj_id, 'libgroups')
        self.annotable = Annotable(self.proj_id, 'libgroups')

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

############################################################
# Assets
############################################################
class Asset(DeclarativeBase):
    """Asset"""
    __tablename__ = "assets"
    __table_args__ = (UniqueConstraint('category_id', 'parent_id', 'name'),
                      ForeignKeyConstraint(['parent_id', 'proj_id'],
                          ['asset_containers.id', 'asset_containers.proj_id']),
                      ForeignKeyConstraint(['taggable_id', 'proj_id'],
                                    ['taggables.id', 'taggables.proj_id']),
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
    taggable_id = Column(Integer)

    # Relations
    project = relation('Project',
                primaryjoin=proj_id==Project.id,
                foreign_keys=[proj_id],
                viewonly=True,
              )
    
    category = relation('Category', backref=backref('assets'))
    
    user = relation('User',
                        primaryjoin=user_id==User.user_id,
                        backref=backref('assets'))

    parent = relation('AssetContainer', backref=backref('assets'))

    submitted_by = relation('User',
                        primaryjoin=submitter_id==User.user_id,
                        backref=backref('submitted_assets'))

    approved_by = relation('User',
                        primaryjoin=approver_id==User.user_id,
                        backref=backref('approved_assets'))
    
    taggable = relation(Taggable, backref='tagged_assets')
    
    # Properties
    @property
    def path(self):
        return os.path.join(self.parent.path, self.category.name, self.name)
    
    @property
    def thumb_path(self):
        name, ext = os.path.splitext(self.name)
        name = name.replace('.#', '')
        name = '%s-thumb.png' % name
        return os.path.join(self.proj_id, G.PREVIEWS, self.parent.path,
                            self.category.name, name)
    
    @property
    def current_ver(self):
        return self.versions[0].ver
    
    @property
    def current_fmtver(self):
        return self.versions[0].fmtver
    
    @property
    def is_sequence(self):
        return G.pattern_seq.match(self.name) and True or False
    
    @property
    def tags(self):
        return self.taggable.tags
    
    # Special methods
    def __init__(self, proj, parent, category, name, user):
        self.proj_id = proj
        self.parent = parent
        self.category = category
        self.name = name
        self.taggable = Taggable(self.proj_id, 'assets')
        
        #create version zero
        AssetVersion(proj, self, 0, user, '')
    
    def __repr__(self):
        return '<Asset: %s>' % (self.id or 0)

    def __json__(self):
        return dict(id=self.id,
                    name=self.name,
                    proj_id=self.proj_id,
                    parent_id=self.parent_id,
                    parent=self.parent,
                    category=self.category,
                    checkedout=self.checkedout,
                    user=self.user,
                    approved=self.approved,
                    path=self.path,
                    current_ver=self.current_ver,
                    current_fmtver=self.current_fmtver,
                    is_sequence=self.is_sequence,
                    thumb_path=self.thumb_path,
                    #'repopath': self.repopath,
                    #'basedir': self.basedir,
                    #'repobasedir': self.repobasedir,
                    #'has_preview': self.has_preview,
                    #'preview_small_repopath': self.preview_small_repopath,
                    #'preview_large_repopath': self.preview_large_repopath,
                    #'status': self.status,
                    #'flow': self.flow,
                    #'waiting_for_approval': self.waiting_for_approval,
                   )


class AssetVersion(DeclarativeBase):
    """Asset version"""
    __tablename__ = "asset_versions"
    __table_args__ = (ForeignKeyConstraint(['annotable_id', 'proj_id'],
                                    ['annotables.id', 'annotables.proj_id']),
                      {})
    
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
    annotable_id = Column(Integer)

    # Relations
    asset = relation('Asset',
                         primaryjoin=and_(asset_id==Asset.id,
                                          proj_id==Asset.proj_id),
                         foreign_keys=[asset_id, proj_id],
                         backref=backref('versions', order_by=desc(ver),
                                         cascade="all, delete, delete-orphan"))
    
    user = relation('User')
    
    annotable = relation(Annotable, backref='annotated_asset_versions')
    
    # Properties
    @property
    def fmtver(self):
        return 'v%03d' % self.ver
    
    @property
    def notes(self):
        return self.annotable.notes
    
    # Special methods
    def __init__(self, proj, asset, ver, user, repoid, has_preview=False,
                                                            preview_ext=None):
        self.proj_id = proj
        self.asset = asset
        self.ver = ver
        self.user = user
        self.repoid = repoid
        #self.has_preview = has_preview
        #self.preview_ext = preview_ext
        self.annotable = Annotable(self.proj_id, 'asset_versions')

    def __repr__(self):
        return '<AssetVersion: "%s" v%03d>' % (self.asset_id, self.ver)

    def __json__(self):
        return {'asset_id': self.asset_id,
                'ver': self.ver,
                'fmtver': self.fmtver,
                'created': self.created.strftime('%Y/%m/%d %H:%M'),
                #'has_preview': self.has_preview,
                #'preview_small_repopath': self.preview_small_repopath,
                #'preview_large_repopath': self.preview_large_repopath,
                #'strftime': self.strftime,
                }


############################################################
# Categories
############################################################
class Category(DeclarativeBase):
    """Asset category"""
    __tablename__ = "categories"
    
    # Columns
    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(Unicode(30), unique=True)
    ordering = Column(Integer)
    naming_convention = Column(Unicode(255))
    
    # Special methods
    def __init__(self, name, ordering=0, naming_convention=''):
        self.name = name
        self.ordering = ordering
        self.naming_convention = naming_convention

    def __repr__(self):
        return '<Category: %s "%s">' % (self.id or 0, self.name)

    def __json__(self):
        return dict(id=self.id,
                    name=self.name,
                    ordering=self.ordering,
                    naming_convention=self.naming_convention,
                   )


class Supervisor(DeclarativeBase):
    """Category supervisor"""
    __tablename__ = "supervisors"
    
    # Columns
    id = Column(Integer, autoincrement=True, primary_key=True)
    proj_id = Column(Unicode(10))
    category_id = Column(Integer)
    user_id = Column(Integer)

    # Relations
    project = relation('Project', primaryjoin=proj_id==Project.id,
                       foreign_keys=[proj_id],
                       backref=backref('supervisors',
                                       collection_class=mapped_list('category',
                                                             targetattr='user')
                                      )
                      )

    category = relation('Category', primaryjoin=category_id==Category.id,
                        foreign_keys=[category_id],
                        backref=backref('supervisors',
                                        collection_class=mapped_list('project',
                                                             targetattr='user')
                                       )
                       )

    user = relation('User', primaryjoin=user_id==User.user_id,
                            foreign_keys=[user_id], backref='_supervisor_for')
    
    # Special methods
    def __init__(self, proj, category, user):
        self.proj_id = proj
        self.category = category
        self.user = user

    def __repr__(self):
        return '<Supervisor: (%s) "%s" %s>' % (self.proj_id, self.category.name,
                                                            self.user.user_name)

    def __json__(self):
        return dict(id=self.id,
                    proj_id=self.proj_id,
                    category_id=self.category_id,
                    user_id=self.user_id,
                   )


class Artist(DeclarativeBase):
    """Category artist"""
    __tablename__ = "artists"
    
    # Columns
    id = Column(Integer, autoincrement=True, primary_key=True)
    proj_id = Column(Unicode(10))
    category_id = Column(Integer)
    user_id = Column(Integer)

    # Relations
    project = relation('Project', primaryjoin=proj_id==Project.id,
                       foreign_keys=[proj_id],
                       backref=backref('artists',
                                       collection_class=mapped_list('category',
                                                             targetattr='user')
                                      )
                      )

    category = relation('Category', primaryjoin=category_id==Category.id,
                        foreign_keys=[category_id],
                        backref=backref('artists',
                                        collection_class=mapped_list('project',
                                                             targetattr='user')
                                       )
                       )

    user = relation('User', primaryjoin=user_id==User.user_id,
                        foreign_keys=[user_id], backref='_artist_for')
    
    # Special methods
    def __init__(self, proj, category, user):
        self.proj_id = proj
        self.category = category
        self.user = user

    def __repr__(self):
        return '<Artist: (%s) "%s" %s>' % (self.proj_id, self.category.name,
                                                            self.user.user_name)

    def __json__(self):
        return dict(id=self.id,
                    proj_id=self.proj_id,
                    category_id=self.category_id,
                    user_id=self.user_id,
                   )


