"""Sharding functions.

Sharding allows to use a different db for each project, the following functions
are used by the session to automatically select the db (or list of dbs) to
query.
"""
from sqlalchemy import Column, Table
from sqlalchemy.sql import ClauseVisitor, operators, Alias, Select

import logging
log = logging.getLogger(__name__)

shards = {}
queries = {'query': [], 'id': []}
common_classes = []
common_tables = set()

def original_froms(selectable):
    if isinstance(selectable, Table):
        return set([selectable])
    elif isinstance(selectable, Alias):
        return original_froms(selectable.original)
    elif isinstance(selectable, Select):
        froms = set()
        for f in selectable.locate_all_froms():
            froms.update(original_froms(f))
        return froms
    else:
        return set()

def shard_chooser(mapper, instance, clause=None):
    """Looks at the given instance and returns a shard id."""
    id_ = None
    if (type(instance) in common_classes) or (instance is None):
        id_ = u'common'
    else:
        id_ = instance.proj_id
    log.debug('shard_chooser: %s' % id_)
    return id_

def id_chooser(query, ident):
    """Given a primary key, returns a list of shards to search."""
    ids = set()
    if original_froms(query.statement) <= common_tables:
        ids = set([u'common'])
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
                    ids.add(u'common')
            elif isinstance(binary.right, Column):
                if binary.right.name=='proj_id':
                    if binary.operator == operators.eq:
                        if callable(binary.left.value):
                            ids.add(binary.left.value())
                        else:
                            ids.add(binary.left.value)
                    elif binary.operator == operators.in_op:
                        for bind in binary.left.clauses:
                            ids.add(bind.value())
            
    if query._criterion is not None:
        FindProject().traverse(query._criterion)
    elif query.statement._whereclause is not None:
        FindProject().traverse(query.statement._whereclause)
    elif original_froms(query.statement) <= common_tables:
        ids =set([u'common'])
    
    if len(ids) == 0:
        ids = set(shards.keys())

    log.debug('query_chooser: %s %s' % (ids, repr(query)))
    return ids

