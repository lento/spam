# -*- coding: utf-8 -*-
"""The application's model objects"""

import datetime, logging
from pylons import cache
from zope.sqlalchemy import ZopeTransactionExtension
from tg import config
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker, lazyload, eagerload
from sqlalchemy.orm.shard import ShardedSession
from sqlalchemy import create_engine, Column
from sqlalchemy.sql import ClauseVisitor, operators


log = logging.getLogger(__name__)

# Base class for all of our model classes (SQLAlchemy's declarative extension)
DeclarativeBase = declarative_base()

# The default metadata is the one from the declarative base.
metadata = DeclarativeBase.metadata


############################################################
# Session
############################################################

# Global session manager: DBSession() returns the Thread-local
# session object appropriate for the current web request.
maker = sessionmaker(autoflush=True, autocommit=False, class_=ShardedSession,
                     extension=ZopeTransactionExtension())

DBSession = scoped_session(maker)


############################################################
# Model modules
############################################################
from spam.model.auth import User, Group, Permission
from spam.model.project import Project, Scene, Shot, LibraryGroup


############################################################
# Caching & helpers
############################################################
def query_projects():
    return DBSession.query(Project).filter_by(archived=False)

def query_projects_archived():
    return DBSession.query(Project).filter_by(archived=True)

def eagerload_maker(proj):
    """Factory for project eagerloaders.
    
    Return a argument-less function suitable for the "createfunc" parameter of
    "Cache.get_value"
    """
    def eagerload_project():
        query = query_projects()
        #query = query.options(eagerload('scenes'), eagerload('libgroups'))
        project = query.filter_by(id=proj).one()
        project.scenes
        project.libgroups
        return (project, datetime.datetime.now())
    return eagerload_project

def get_project(proj):
    """Return a project eagerloaded with its scenes and libgroups
    
    "get_project" keeps a (thread-local) cache of loaded projects, reloading
    instances from the db if the "modified" field is newer then the cache
    """
    # get a lazyload instance of the project, save the modified time and discard
    curproject = query_projects().filter_by(id=proj).one()
    modified = curproject.modified
    DBSession.expunge(curproject)
    
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
    
    # put the instance back into the session
    if project not in DBSession:
        DBSession.add(project)
    
    return project


######################################################################
# Sharding
# 
# This allows to use a different db for each project, the following functions
# are used by the session to automatically select the db (or list of dbs) to
# query.
######################################################################

shards = {}
queries = {'query': [], 'id': []}
common_tables = set([Project.__table__, User.__table__, Group.__table__,
                     Permission.__table__,])

def shard_chooser(mapper, instance, clause=None):
    """Looks at the given instance and returns a shard id."""
    log.debug('shard_chooser 0: %s, %s, %s' % (mapper, instance, clause))
    if isinstance(instance, Project) or (instance is None):
        return 'common'
    else:
        return instance.proj_id

def id_chooser(query, ident):
    """Given a primary key, returns a list of shards to search."""
    ids = set()
    log.debug('id_chooser 0: %s, %s' % (query, ident))
    if query.statement.locate_all_froms() <= common_tables:
        ids = set(['common'])
    else:
        ids = set(shards.keys())
    
    log.debug('id_chooser 1: %s' % ids)
    return ids

def query_chooser(query):
    """
    Returns a list of shard ids.
    
    Can just be all of them, but here we'll search into the Query in order
    to try to narrow down the list of shards to query.
    """
    log.debug('query_chooser 0: %s' % query)
    queries['query'].append(query)
    ids = set()
    
    class FindProject(ClauseVisitor):
        def visit_binary(self, binary):
            """
            Traverse through the query's criterion, searching for SQL
            constructs. We'll grab project nicks as we find them
            and convert to shard ids
            """
            if isinstance(binary.left, Column):
                if binary.left.name=='proj_id' and binary.right.value:
                    if binary.operator == operators.eq:
                        if callable(binary.right.value):
                            ids.add(binary.right.value())
                        else:
                            ids.add(binary.right.value)
                    elif binary.operator == operators.in_op:
                        for bind in binary.right.clauses:
                            if callable(bind.value):
                                ids.add(bind.value())
                            else:
                                ids.add(bind.value)
                elif binary.left.table in common_tables:
                    ids.add('common')
            elif isinstance(binary.right, Column):
                if binary.right.name=='proj_id':
                    if (binary.operator == operators.eq and
                                                callable(binary.left.value)):
                        ids.add(binary.left.value())
                    elif binary.operator == operators.in_op:
                        for bind in binary.left.clauses:
                            ids.add(bind.value())
            
    if query._criterion:
        FindProject().traverse(query._criterion)
    elif query.statement.locate_all_froms() <= common_tables:
        ids =set(['common'])
    
    if len(ids) == 0:
        ids = set(shards.keys())

    log.debug('query_chooser 1: %s' % ids)
    return ids


############################################################
# Init model
############################################################
def init_model(engine):
    """Call me before using any of the tables or classes in the model."""

    shards['common'] = engine
    echo = True
    
    DBSession.configure(shards=shards)
    DBSession.configure(shard_chooser=shard_chooser, id_chooser=id_chooser,
                                                    query_chooser=query_chooser)
    
    sess = DBSession()
    pq = sess.query(Project)
    for p in pq:
        #log.debug('add shard: %s' % p.id)
        db_url_tmpl = config.get('db_url_tmpl', 'sqlite:///db/spam_%s.sqlite')
        db = create_engine(db_url_tmpl % p.id, echo=echo)
        sess.bind_shard(p.id, db)
        shards[p.id] = db




