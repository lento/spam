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

# Utils
from utils import MappedList, mapped_list

# Global session manager: DBSession() returns the Thread-local
# session object appropriate for the current web request.
maker = sessionmaker(autoflush=True, autocommit=False,
                     extension=ZopeTransactionExtension())
DBSession = scoped_session(maker)

# Migrate versioning
from versioning import db_init, migraterepo_get_version, db_get_version
from versioning import db_upgrade, db_downgrade

# Models import
from auth import User, Group, Permission, group_permission_table
from auth import user_group_table
from project import Project, Scene, Shot, LibraryGroup, Asset, AssetVersion
from project import project_user_table, project_admin_table
from project import Category, Supervisor, Artist, Tag, Taggable, Note

# Caching & helpers
from helpers import query_projects, query_projects_archived, project_get
from helpers import project_get_eager, session_get, scene_get, shot_get
from helpers import container_get, asset_get, category_get, libgroup_get
from helpers import group_get, tag_get, user_get

# Init model
def init_model(engine):
    """Call me before using any of the tables or classes in the model."""
    
    DBSession.configure(bind=engine)

