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

# Sharding
from sharding import shards, queries, shard_chooser, id_chooser, query_chooser

# Global session manager: DBSession() returns the Thread-local
# session object appropriate for the current web request.
maker = sessionmaker(autoflush=True, autocommit=False, class_=ShardedSession,
                     extension=ZopeTransactionExtension(),
                     shard_chooser=shard_chooser, id_chooser=id_chooser,
                     query_chooser=query_chooser)
DBSession = scoped_session(maker)

# Migrate versioning
from versioning import db_init, migraterepo_get_version, db_get_version
from versioning import db_upgrade, db_downgrade

# Models import
from auth import User, Group, Permission, group_permission_table
from auth import user_group_table
from project import Project, Scene, Shot, LibraryGroup, Asset, AssetCategory
from project import AssetVersion, project_user_table, project_admin_table

# Set which classes and tables belong to the common db
sharding.common_classes = [User, Group, Permission, Project, AssetCategory]
sharding.common_tables = set([User.__table__,
                              Group.__table__,
                              Permission.__table__,
                              group_permission_table,
                              user_group_table,
                              Project.__table__,
                              project_user_table,
                              project_admin_table,
                              AssetCategory.__table__,
                             ])

# Caching & helpers
from util import query_projects, query_projects_archived, project_get
from util import project_get_eager, session_get, scene_get, shot_get, add_shard
from util import container_get, asset_get, category_get, libgroup_get, user_get

# Init model
def init_model(engine):
    """Call me before using any of the tables or classes in the model."""
    sharding.shards[u'common'] = engine
    
    DBSession.configure(shards=sharding.shards)

