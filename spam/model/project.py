# -*- coding: utf-8 -*-
#
# SPAM Spark Project & Asset Manager
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 3 of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this program; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place - Suite 330,
# Boston, MA 02111-1307, USA.
#
# Original Copyright (c) 2010, Lorenzo Pierfederici <lpierfederici@gmail.com>
# Contributor(s): 
#
"""
Project data model.

This is where the model for project data is defined.
"""

import os.path
from datetime import datetime
from hashlib import sha1

from sqlalchemy import Table, ForeignKey, Column, UniqueConstraint
from sqlalchemy import ForeignKeyConstraint, and_, desc
from sqlalchemy.types import Unicode, UnicodeText, Integer, DateTime, Boolean
from sqlalchemy.types import String
from sqlalchemy.orm import relation, synonym, backref

from tg import app_globals as G, config
from spam.model import DeclarativeBase, metadata, mapped_list
from spam.model import migraterepo_get_version, db_get_version
from spam.model import db_upgrade, db_downgrade
from spam.model.auth import User

import logging
log = logging.getLogger(__name__)


############################################################
# Association tables
############################################################

# Association table for the many-to-many relationship projects-admins.
projects_admins_table = Table('__projects_admins', metadata,
    Column('project_id', Unicode(10), ForeignKey('projects.id',
                                    onupdate="CASCADE", ondelete="CASCADE")),
    Column('user_id', Unicode(40), ForeignKey('users.user_id',
                                    onupdate="CASCADE", ondelete="CASCADE")),
)


############################################################
# Journal
############################################################
class Journal(DeclarativeBase):
    __tablename__ = 'journal'
    
    # Columns
    id = Column(String(40), primary_key=True)
    domain = Column(Unicode(24))
    user_id = Column(Unicode(40), ForeignKey('users.user_id'))
    text = Column(UnicodeText)
    created = Column(DateTime, default=datetime.now)
    
    # Relations
    user = relation('User', backref=backref('journal',
                                                    order_by=desc('created')))
    
    # Special methods
    def __init__(self, user, text):
        self.domain = config.auth_domain
        self.user = user
        self.text = text
        self.created = datetime.now()
        hashable = '%s-%s-%s' % (self.created, self.user_id, self.text)
        self.id = sha1(hashable).hexdigest()

    def __repr__(self):
        return '<Journal: (%s) %s: "%s">' % (self.created, self.user_id,
                                                                    self.text)

    def __json__(self):
        return dict(id=self.id,
                    domain=self.domain,
                    user=self.user,
                    test=self.text,
                    created=self.created,
                   )

############################################################
# Tags
############################################################
# Association table for the many-to-many relationship taggables-tags.
taggables_tags_table = Table('__taggables_tags', metadata,
    Column('taggable_id', String(40), ForeignKey('taggables.id',
                                    onupdate='CASCADE', ondelete='CASCADE')),
    Column('tag_id', Unicode(40), ForeignKey('tags.id',
                                    onupdate='CASCADE', ondelete='CASCADE')),
)

class Taggable(DeclarativeBase):
    __tablename__ = 'taggables'
    
    # Columns
    id = Column(String(40), primary_key=True)
    association_type = Column(Unicode(50))
    
    # Properties
    @property
    def tagged(self):
        return getattr(self, 'tagged_%s' % self.association_type)
    
    # Special methods
    def __init__(self, id, association_type):
        self.id = id
        self.association_type = association_type

    def __repr__(self):
        return '<Taggable %s: %s>' % (self.id,
            dict(association_type=self.association_type))


class Tag(DeclarativeBase):
    __tablename__ = 'tags'
    
    # Columns
    id = Column(Unicode(40), primary_key=True)
    created = Column(DateTime, default=datetime.now)
    
    # Relations
    taggables = relation(Taggable, secondary=taggables_tags_table,
                                backref=backref('tags', order_by='Tag.id'))
    
    # Properties
    @property
    def tagged(self):
        return [t.tagged for t in self.taggables]
    
    # Special methods
    def __init__(self, id):
        self.id = id

    def __repr__(self):
        return '<Tag: %s>' % self.id

    def __json__(self):
        return {'id': self.id,
                'created': self.created,
               }

############################################################
# Notes
############################################################
class Annotable(DeclarativeBase):
    __tablename__ = 'annotables'
    
    # Columns
    id = Column(String(40), primary_key=True)
    association_type = Column(Unicode(50))
    
    # Properties
    @property
    def annotated(self):
        return getattr(self, 'annotated_%s' % self.association_type)
    
    # Special methods
    def __init__(self, id, association_type):
        self.id = id
        self.association_type = association_type

    def __repr__(self):
        return '<Annotable: %s (%s)>' % (self.id, self.association_type)


class Note(DeclarativeBase):
    __tablename__ = 'notes'
    
    # Columns
    id = Column(String(40), primary_key=True)
    annotable_id = Column(String(40), ForeignKey('annotables.id'))
    user_id = Column(Unicode(40), ForeignKey('users.user_id'))
    text = Column(UnicodeText)
    created = Column(DateTime, default=datetime.now)
    sticky = Column(Boolean, default=False)

    # Relations
    user = relation('User', backref=backref('notes', order_by=desc('created')))
    
    annotable = relation(Annotable,
                            backref=backref('notes', order_by=desc('created')))
    
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
    def __init__(self, user, text):
        self.created = datetime.now()
        self.user = user
        self.text = text
        hashable = '%s-%s-%s' % (self.user_id, self.created, self.text)
        self.id = sha1(hashable).hexdigest()

    def __repr__(self):
        return '<Note: by %s at %s "%s">' % (self.user.user_name,
                                                self.strftime,
                                                self.summary)

    def __json__(self):
        return {'id': self.id,
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
    name = Column(Unicode(40), unique=True)
    description = Column(Unicode)
    created = Column(DateTime, default=datetime.now)
    modified = Column(DateTime, default=datetime.now)
    archived = Column(Boolean, default=False)
    
    # Relations
    admins = relation('User', secondary=projects_admins_table,
                                                    backref='projects_as_admin')
    
    # Properties
    @property
    def users(self):
        return (set([s.user for s in self.supervisors]) |
                set([a.user for a in self.artists]) |
                set(self.admins))
    
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
        self.name = name or id
        self.description = description

    def __repr__(self):
        return '<Project %s: %s>' % (self.id,
            dict(name=self.name,
                 description=self.description,
                 archived=self.archived,
                ))
    
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
    id = Column(String(40), primary_key=True)
    discriminator = Column('type', Unicode(20))
    __mapper_args__ = {'polymorphic_on': discriminator}

    # Special methods
    def __repr__(self):
        return '<AssetContainer: %s (%s)>' % (self.id, self.discriminator)

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
    created = Column(DateTime, default=datetime.now)

    # Relations
    project = relation('Project', viewonly=True,
                       backref=backref('scenes', viewonly=True, order_by=name)
                      )
    
    taggable = relation(Taggable,
                            backref=backref('tagged_scene', uselist=False))
    
    annotable = relation(Annotable,
                            backref=backref('annotated_scene', uselist=False))
    
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
        self.id = sha1('%s-%s' % (self.proj_id, self.name)).hexdigest()
        self.description = description
        self.taggable = Taggable(self.id, 'scene')
        self.annotable = Annotable(self.id, 'scene')

    def __repr__(self):
        return '<Scene %s (%s): %s>' % (self.id, self.path,
            dict(proj_id=self.proj_id,
                 name=self.name,
                 description=self.description,
                ))

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
    __table_args__ = (UniqueConstraint('parent_id', 'name'),
                      ForeignKeyConstraint(['id'], ['taggables.id']),
                      ForeignKeyConstraint(['id'], ['annotables.id']),
                      {})
    __mapper_args__ = {'polymorphic_identity': 'shot'}
    
    # Columns
    id = Column(String(40), ForeignKey('asset_containers.id'), primary_key=True)
    parent_id = Column(String(40), ForeignKey('scenes.id'))
    name = Column(Unicode(15))
    created = Column(DateTime, default=datetime.now)
    description = Column(UnicodeText)
    location = Column(Unicode(255))
    action = Column(UnicodeText)
    frames = Column(Integer)
    handle_in = Column(Integer)
    handle_out = Column(Integer)
    
    # Relations
    parent = relation(Scene,
                        backref=backref('shots', order_by=name, lazy=False))
    
    taggable = relation(Taggable, backref=backref('tagged_shot', uselist=False))
    
    annotable = relation(Annotable, backref=backref('annotated_shot',
                                                                uselist=False))
    
    # Properties
    @property
    def project(self):
        return self.parent.project
    
    @property
    def proj_id(self):
        return self.parent.proj_id
    
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
    def __init__(self, parent, name, description=None, action=None,
                       location=None, frames=0, handle_in=0, handle_out=0):
        self.parent = parent
        self.name = name
        self.description = description
        self.location = location
        self.frames = frames
        self.handle_in = handle_in
        self.handle_out = handle_out
        self.action = action
        hashable = '%s-%s' % (parent.id, self.name)
        log.debug('Shot.__init__: %s' % hashable)
        self.id = sha1(hashable).hexdigest()
        self.taggable = Taggable(self.id, 'shot')
        self.annotable = Annotable(self.id, 'shot')

    def __repr__(self):
        return '<Shot %s (%s): %s>' % (self.id, self.name,
            dict(proj_id=self.proj_id,
                 parent_id=self.parent_id,
                 name=self.name,
                 description=self.description,
                 location=self.location,
                 action=self.action,
                 frames=self.frames,
                 handle_in=self.handle_in,
                 handle_out=self.handle_out,
                ))

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
    
    # Relations
    project = relation('Project',  backref=backref('libgroups', primaryjoin=
        'and_(Project.id==LibraryGroup.proj_id, LibraryGroup.parent_id==None)',
        viewonly=True, order_by=name))
    
    subgroups = relation('LibraryGroup', primaryjoin=parent_id==id,
                             foreign_keys=[parent_id], lazy=False, join_depth=5,
                             backref=backref('parent', remote_side=[id]))
    
    taggable = relation(Taggable, backref=backref('tagged_libgroup',
                                                                uselist=False))
    
    annotable = relation(Annotable, backref=backref('annotated_libgroup',
                                                                uselist=False))
    
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
        hashable = '%s-%s' % (self.parent_id, self.name)
        self.id = sha1(hashable).hexdigest()
        self.taggable = Taggable(self.id, 'libgroup')
        self.annotable = Annotable(self.id, 'libgroup')

    def __repr__(self):
        return '<LibraryGroup %s (%s): %s>' % (self.id, self.path,
                dict(proj_id=self.proj_id,
                     parent_id=self.parent_id,
                     name=self.name,
                     description=self.description,
                    ))

    def __json__(self):
        return dict(id=self.id,
                    proj_id=self.proj_id,
                    parent_id=self.parent_id,
                    name=self.name,
                    description=self.description,
                    #created=self.created.strftime('%Y/%m/%d %H:%M'),
                   )

############################################################
# Categories
############################################################
class Category(DeclarativeBase):
    """Asset category"""
    __tablename__ = "categories"
    
    # Columns
    id = Column(Unicode(40), primary_key=True)
    ordering = Column(Integer)
    naming_convention = Column(Unicode(255))
    
    # Special methods
    def __init__(self, id, ordering=0, naming_convention=''):
        self.id = id
        self.ordering = ordering
        self.naming_convention = naming_convention

    def __repr__(self):
        return '<Category %s: %s>' % (self.id,
            dict(ordering=self.ordering,
                 naming_convention=self.naming_convention
                ))

    def __json__(self):
        return dict(id=self.id,
                    ordering=self.ordering,
                    naming_convention=self.naming_convention,
                   )


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

    # Relations
    project = relation('Project', backref=backref('supervisors',
                collection_class=mapped_list('category', targetattr='user')))

    category = relation('Category', backref=backref('supervisors',
                collection_class=mapped_list('project', targetattr='user')))

    user = relation('User', backref='_supervisor_for')
    
    # Special methods
    def __init__(self, proj, category, user):
        self.proj_id = proj
        self.category = category
        self.user = user
        hashable = '%s-%s-%s' % (proj, category.id, user.user_id)
        self.id = sha1(hashable).hexdigest()

    def __repr__(self):
        return '<Supervisor: (%s) "%s" %s>' % (self.proj_id, self.category.id,
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
    __table_args__ = (UniqueConstraint('proj_id', 'category_id', 'user_id'),
                      {})
    
    # Columns
    id = Column(String(40), primary_key=True)
    proj_id = Column(Unicode(10), ForeignKey('projects.id'))
    category_id = Column(Unicode(40), ForeignKey('categories.id'))
    user_id = Column(Unicode(40), ForeignKey('users.user_id'))

    # Relations
    project = relation('Project', backref=backref('artists',
                collection_class=mapped_list('category', targetattr='user')))

    category = relation('Category', backref=backref('artists',
                collection_class=mapped_list('project', targetattr='user')))

    user = relation('User', backref='_artist_for')
    
    # Special methods
    def __init__(self, proj, category, user):
        self.proj_id = proj
        self.category = category
        self.user = user
        hashable = '%s-%s-%s' % (proj, category.id, user.user_id)
        self.id = sha1(hashable).hexdigest()

    def __repr__(self):
        return '<Artist: (%s) "%s" %s>' % (self.proj_id, self.category.id,
                                                            self.user.user_name)

    def __json__(self):
        return dict(id=self.id,
                    proj_id=self.proj_id,
                    category_id=self.category_id,
                    user_id=self.user_id,
                   )

############################################################
# Assets
############################################################
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
    user_id = Column(Integer, ForeignKey('users.user_id'))

    # Relations
    category = relation('Category', backref=backref('assets'))
    
    user = relation('User',
                        primaryjoin=user_id==User.user_id,
                        backref=backref('assets'))

    parent = relation('AssetContainer', backref=backref('assets'))

    taggable = relation(Taggable, backref='tagged_asset')
    
    # Properties
    @property
    def proj_id(self):
        return self.parent.project.id
    
    @property
    def project(self):
        return self.parent.project
    
    @property
    def path(self):
        return os.path.join(self.parent.path, self.category.id, self.name)
    
    @property
    def thumb_path(self):
        name, ext = os.path.splitext(self.name)
        name = name.replace('.#', '')
        name = '%s-thumb.png' % name
        return os.path.join(self.proj_id, G.PREVIEWS, self.parent.path,
                            self.category.id, name)
    
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
    def __init__(self, parent, category, name, user):
        self.parent = parent
        self.category = category
        self.name = name
        hashable = '%s-%s-%s' % (parent.id, category.id, name)
        self.id = sha1(hashable).hexdigest()
        self.taggable = Taggable(self.id, 'asset')
        
        #create version zero
        AssetVersion(self, 0, user, '')
    
    def __repr__(self):
        return '<Asset: %s (%s)>' % (self.id, self.name)

    def __json__(self):
        return dict(id=self.id,
                    name=self.name,
                    proj_id=self.proj_id,
                    parent_id=self.parent_id,
                    parent=self.parent,
                    category=self.category,
                    checkedout=self.checkedout,
                    user=self.user,
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
    __table_args__ = (UniqueConstraint('asset_id', 'ver'),
                      ForeignKeyConstraint(['id'], ['annotables.id']),
                      {})
    
    # Columns
    id = Column(String(40), primary_key=True)
    asset_id = Column(String(40), ForeignKey('assets.id'))
    ver = Column(Integer)
    created = Column(DateTime, default=datetime.now)
    repoid = Column(String(50))
    #has_preview = Column(Boolean)
    #preview_ext = Column(String(10))
    user_id = Column(Integer, ForeignKey('users.user_id'))

    # Relations
    asset = relation('Asset', backref=backref('versions', order_by=desc(ver),
                                         cascade="all, delete, delete-orphan"))
    
    user = relation('User')
    
    annotable = relation(Annotable, backref='annotated_asset_version')
    
    # Properties
    @property
    def fmtver(self):
        return 'v%03d' % self.ver
    
    @property
    def notes(self):
        return self.annotable.notes
    
    # Special methods
    def __init__(self, asset, ver, user, repoid, has_preview=False,
                                                            preview_ext=None):
        self.asset = asset
        self.ver = ver
        self.user = user
        self.repoid = repoid
        #self.has_preview = has_preview
        #self.preview_ext = preview_ext
        hashable = '%s-%s' % (asset.id, ver)
        self.id = sha1(hashable).hexdigest()
        self.annotable = Annotable(self.id, 'asset_version')

    def __repr__(self):
        return '<AssetVersion: %s (%s_v%03d)>' % (self.asset_id,
                                                    self.asset.name, self.ver)

    def __json__(self):
        return dict(id=self.id,
                    asset_id=self.asset_id,
                    ver=self.ver,
                    fmtver=self.fmtver,
                    created=self.created.strftime('%Y/%m/%d %H:%M'),
                    #'has_preview': self.has_preview,
                    #'preview_small_repopath': self.preview_small_repopath,
                    #'preview_large_repopath': self.preview_large_repopath,
                    #'strftime': self.strftime,
                   )

