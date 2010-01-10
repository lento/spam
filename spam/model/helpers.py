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
"""Caching & helpers"""

from datetime import datetime
from pylons import cache
from tg import config
from sqlalchemy import create_engine
from sqlalchemy.exceptions import InvalidRequestError
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from spam.lib.exceptions import SPAMDBError, SPAMDBNotFound
from spam.model import DBSession, Project, Scene, Shot, LibraryGroup, Asset
from spam.model import Category, User, Group, Taggable, Tag

import logging
log = logging.getLogger(__name__)

# Helpers
def session_get():
    """Return a session for the current thread."""
    return DBSession()

def query_projects():
    """Return a ``query`` object filtering `active` projects."""
    return session_get().query(Project).filter_by(archived=False)

def query_projects_archived():
    """Return a ``query`` object filtering `archived` projects."""
    return session_get().query(Project).filter_by(archived=True)

def user_get(user_id):
    """Return a user."""
    query = session_get().query(User).filter_by(user_id=user_id)
    try:
        return query.one()
    except NoResultFound:
        raise SPAMDBNotFound('User "%s" could not be found.' % user_id)
    except MultipleResultsFound:
        raise SPAMDBError('Error when searching user "%s".' % user_id)

def group_get(group_id):
    """Return a group."""
    query = session_get().query(Group).filter_by(group_id=group_id)
    try:
        return query.one()
    except NoResultFound:
        raise SPAMDBNotFound('Group "%s" could not be found.' % group_id)
    except MultipleResultsFound:
        raise SPAMDBError('Error when searching group "%s".' % group_id)

def project_get(proj):
    """Return a lazyloaded project."""
    try:
        return query_projects().filter_by(id=proj).one()
    except NoResultFound:
        raise SPAMDBNotFound('Project "%s" could not be found.' % proj)
    except MultipleResultsFound:
        raise SPAMDBError('Error when searching project "%s".' % proj)

def scene_get(proj, sc):
    """Return a scene."""
    query = session_get().query(Scene)
    try:
        return query.filter_by(proj_id=proj).filter_by(name=sc).one()
    except NoResultFound:
        raise SPAMDBNotFound('Scene "%s" could not be found.' % sc)
    except MultipleResultsFound:
        raise SPAMDBError('Error when searching scene "%s".' % sc)

def shot_get(proj, sc, sh):
    """Return a shot."""
    scene = scene_get(proj, sc)
    query = session_get().query(Shot)
    try:
        return query.filter_by(parent_id=scene.id).filter_by(name=sh).one()
    except NoResultFound:
        raise SPAMDBNotFound('Shot "%s" could not be found.' % sh)
    except MultipleResultsFound:
        raise SPAMDBError('Error when searching shot "%s".' % sh)

def libgroup_get(proj, libgroup_id):
    """Return a libgroup."""
    query = session_get().query(LibraryGroup).filter_by(proj_id=proj)
    try:
        return query.filter_by(id=libgroup_id).one()
    except NoResultFound:
        raise SPAMDBNotFound('LibraryGroup "%s" could not be found.' % libgroup_id)
    except MultipleResultsFound:
        raise SPAMDBError('Error when searching Librarygroup "%s".' % libgroup_id)

def container_get(proj, container_type, container_id):
    """Return a container."""
    if container_type=='shot':
        query = session_get().query(Shot)
    elif container_type=='libgroup':
        query = session_get().query(LibraryGroup)
    try:
        return query.filter_by(id=container_id).one()
    except NoResultFound:
        raise SPAMDBNotFound('Container "%s %s" could not be found.' %
                                                (container_type, container_id))
    except MultipleResultsFound:
        raise SPAMDBError('Error when searching container "%s %s".' %
                                                (container_type, container_id))

def asset_get(proj, asset_id):
    """Return an asset."""
    query = session_get().query(Asset)
    try:
        return query.filter_by(id=asset_id).one()
    except NoResultFound:
        raise SPAMDBNotFound('Asset "%s" could not be found.' % asset_id)
    except MultipleResultsFound:
        raise SPAMDBError('Error when searching asset "%s".' % asset_id)

def category_get(category_id):
    """Return a asset category."""
    query = session_get().query(Category).filter_by(id=category_id)
    try:
        return query.one()
    except NoResultFound:
        raise SPAMDBNotFound('Category "%s" could not be found.' % category_id)
    except MultipleResultsFound:
        raise SPAMDBError('Error when searching category "%s".' % category_id)

def taggable_get(taggable_id):
    """Return an existing taggable."""
    query = session_get().query(Taggable).filter_by(id=taggable_id)
    try:
        return query.one()
    except NoResultFound:
        return SPAMDBNotFound('Taggable "%s" could not be found.' % taggable_id)
    except MultipleResultsFound:
        raise SPAMDBError('Error when searching taggable "%s".' % taggable_id)

def tag_get(tag_id):
    """Return an existing tag or creates a new one."""
    query = session_get().query(Tag).filter_by(id=tag_id)
    try:
        return query.one()
    except NoResultFound:
        return Tag(tag_id)
    except MultipleResultsFound:
        raise SPAMDBError('Error when searching tag "%s".' % tag_id)

# Cache
def eagerload_maker(proj):
    """Factory for project eagerloaders.
    
    Return a argument-less function suitable for the ``createfunc`` parameter of
    ``Cache.get_value``
    """
    def eagerload_project():
        try:
            project = query_projects().filter_by(id=proj).one()
        except (NoResultFound, MultipleResultsFound):
            raise SPAMProjectNotFound('Project "%s" could not be found.' % proj)
        project.scenes
        project.libgroups
        return (project, datetime.now())
    return eagerload_project

def project_get_eager(proj):
    """Return a project eagerloaded with its scenes and libgroups
    
    ``project_get_eager`` keeps a (thread-local) cache of loaded projects,
    reloading instances from the db if the "modified" field is newer then the
    cache.
    """
    session = session_get()
    
    # get a lazyload instance of the project, save the modified time and discard
    curproject = project_get(proj)
    modified = curproject.modified
    session.expunge(curproject)
    
    # get the project from cache
    projcache = cache.get_cache('projects')
    project, cached = projcache.get_value(key=proj,
                                  createfunc=eagerload_maker(proj),
                                  expiretime=360)

    # check if its older then the db
    if cached < modified:
        # remove the invalidated value from the cache and reload from db
        projcache.remove_value(proj)
        project, cached = projcache.get_value(key=proj,
                                  createfunc=eagerload_maker(proj),
                                  expiretime=360)
    
    # put project back into the session if necessary
    try:
        session.add(project)
    except InvalidRequestError:
        pass
    
    return project

