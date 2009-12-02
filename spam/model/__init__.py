# -*- coding: utf-8 -*-
"""The application's model objects"""
from zope.sqlalchemy import ZopeTransactionExtension
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker, lazyload, eagerload
from sqlalchemy.orm.shard import ShardedSession

# Base class for all of our model classes (SQLAlchemy's declarative extension)
DeclarativeBase = declarative_base()

# The default metadata is the one from the declarative base.
metadata = DeclarativeBase.metadata

# Global session manager: DBSession() returns the Thread-local
# session object appropriate for the current web request.
maker = sessionmaker(autoflush=True, autocommit=False, class_=ShardedSession,
                     extension=ZopeTransactionExtension())
DBSession = scoped_session(maker)

# Migrate versioning
from versioning import db_init, migraterepo_get_version, db_get_version
from versioning import db_upgrade, db_downgrade

# Models import
from auth import User, Group, Permission
from project import Project, Scene, Shot, LibraryGroup, Asset, AssetCategory
from project import AssetVersion

# Caching & helpers
from util import query_projects, query_projects_archived, project_get
from util import project_get_eager, session_get, add_shard, scene_get, shot_get

# Sharding
from sharding import shards, queries, shard_chooser, id_chooser, query_chooser

# Init model
def init_model(engine):
    """Call me before using any of the tables or classes in the model."""

    shards[u'common'] = engine
    
    DBSession.configure(shards=shards)
    DBSession.configure(shard_chooser=shard_chooser, id_chooser=id_chooser,
                                                    query_chooser=query_chooser)

