# -*- coding: utf-8 -*-
"""The application's model objects"""

from pylons import cache
from zope.sqlalchemy import ZopeTransactionExtension
from tg import config
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker, lazyload, eagerload
from sqlalchemy.orm.shard import ShardedSession
from sqlalchemy import create_engine, Column
from sqlalchemy.sql import ClauseVisitor, operators

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
# Caching
############################################################
def eagerload_project(proj):
    query = DBSession.query(Project)
    query = query.options(eagerload('scenes'), eagerload('libgroups'))
    return query.get(proj)

def get_project(proj):
    projcache = cache.get_cache('projects')
    project = projcache.get_value(key=proj,
                                  createfunc=lambda: eagerload_project(proj),
                                  type='memory',
                                  expiretime=120)
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
    print('shard_chooser 0:', mapper, instance, clause)
    if isinstance(instance, Project):
        return 'common'
    else:
        return instance.proj_id

def id_chooser(query, ident):
    """Given a primary key, returns a list of shards to search."""
    ids = []
    print('id_chooser 0:', query, ident)
    if query.statement.locate_all_froms() <= common_tables:
        ids =['common']
    else:
        ids = shards.keys()
    
    print('id_chooser 1:', ids)
    return ids

def query_chooser(query):
    """
    Returns a list of shard ids.
    
    Can just be all of them, but here we'll search into the Query in order
    to try to narrow down the list of shards to query.
    """
    print('query_chooser 0:', query)
    queries['query'].append(query)
    ids = []
    
    class FindProject(ClauseVisitor):
        def visit_binary(self, binary):
            """
            Traverse through the query's criterion, searching for SQL
            constructs. We'll grab project nicks as we find them
            and convert to shard ids
            """
            if isinstance(binary.left, Column):
                if binary.left.name=='proj_id':
                    if binary.operator == operators.eq and binary.right.value:
                        ids.append(binary.right.value)
                    elif binary.operator == operators.in_op:
                        for bind in binary.right.clauses:
                            ids.append(bind.value)
                elif binary.left.table in common_tables:
                    ids.append('common')
            elif isinstance(binary.right, Column):
                if binary.right.name=='proj_id':
                    if (binary.operator == operators.eq and
                                                callable(binary.left.value)):
                        ids.append(binary.left.value())
                    elif binary.operator == operators.in_op:
                        for bind in binary.left.clauses:
                            ids.append(bind.value())
            
    if query._criterion:
        FindProject().traverse(query._criterion)
    elif query.statement.locate_all_froms() <= common_tables:
        ids =['common']
    
    if len(ids) == 0:
        ids = shards.keys()

    #print('query_chooser 1:', ids)
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
    pq = sess.query(Project).options(lazyload('scenes'), lazyload('libgroups'))
    for p in pq:
        #print('add shard: ', p.id)
        db_url_tmpl = config.get('db_url_tmpl', 'sqlite:///db/spam_%s.sqlite')
        db = create_engine(db_url_tmpl % p.id, echo=echo)
        sess.bind_shard(p.id, db)
        shards[p.id] = db




