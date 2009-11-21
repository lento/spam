"""Sharding functions.

Sharding allows to use a different db for each project, the following functions
are used by the session to automatically select the db (or list of dbs) to
query.
"""
from tg import config
from sqlalchemy import create_engine, Column
from sqlalchemy.sql import ClauseVisitor, operators
from spam.model import DBSession, Project, User, Group, Permission, echo

import logging
log = logging.getLogger(__name__)

shards = {}
queries = {'query': [], 'id': []}
common_tables = set([Project.__table__, User.__table__, Group.__table__,
                     Permission.__table__,])

def shard_chooser(mapper, instance, clause=None):
    """Looks at the given instance and returns a shard id."""
    id_ = None
    if isinstance(instance, Project) or (instance is None):
        id_ = 'common'
    else:
        id_ = instance.proj_id
    log.debug('shard_chooser: %s' % id_)
    return id_

def id_chooser(query, ident):
    """Given a primary key, returns a list of shards to search."""
    ids = set()
    if query.statement.locate_all_froms() <= common_tables:
        ids = set(['common'])
    else:
        ids = set(shards.keys())
    
    log.debug('id_chooser: %s' % ids)
    return ids

def query_chooser(query):
    """
    Returns a list of shard ids.
    
    Can just be all of them, but here we'll search into the Query in order
    to try to narrow down the list of shards to query.
    """
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

    log.debug('query_chooser: %s' % ids)
    return ids

def add_shard(proj):
    db_url_tmpl = config.get('db_url_tmpl', 'sqlite:///db/spam_%s.sqlite')
    db = create_engine(db_url_tmpl % proj, echo=echo)
    DBSession().bind_shard(proj, db)
    shards[proj] = db

