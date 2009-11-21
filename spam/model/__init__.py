# -*- coding: utf-8 -*-
"""The application's model objects"""
from zope.sqlalchemy import ZopeTransactionExtension
from tg import config
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker, lazyload, eagerload
from sqlalchemy.orm.shard import ShardedSession
from sqlalchemy import create_engine

# Base class for all of our model classes (SQLAlchemy's declarative extension)
DeclarativeBase = declarative_base()


# The default metadata is the one from the declarative base.
metadata = DeclarativeBase.metadata


# Global session manager: DBSession() returns the Thread-local
# session object appropriate for the current web request.
maker = sessionmaker(autoflush=True, autocommit=False, class_=ShardedSession,
                     extension=ZopeTransactionExtension())
DBSession = scoped_session(maker)


# Models import
from auth import User, Group, Permission
from project import Project, Scene, Shot, LibraryGroup


# Caching & helpers
from util import query_projects, query_projects_archived, get_project


# Sharding
from sharding import shards, queries, shard_chooser, id_chooser, query_chooser


# Init model
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
        db_url_tmpl = config.get('db_url_tmpl', 'sqlite:///db/spam_%s.sqlite')
        db = create_engine(db_url_tmpl % p.id, echo=echo)
        sess.bind_shard(p.id, db)
        shards[p.id] = db




