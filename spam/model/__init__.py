# -*- coding: utf-8 -*-
#
# This file is part of SPAM (Spark Project & Asset Manager).
#
# SPAM is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# SPAM is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with SPAM.  If not, see <http://www.gnu.org/licenses/>.
#
# Original Copyright (c) 2010, Lorenzo Pierfederici <lpierfederici@gmail.com>
# Contributor(s): 
#
"""The application's model objects"""

from zope.sqlalchemy import ZopeTransactionExtension
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker, lazyload, eagerload

# Base class for all of our model classes (SQLAlchemy's declarative extension)
DeclarativeBase = declarative_base()

# The default metadata is the one from the declarative base.
metadata = DeclarativeBase.metadata

# Utils
from utils import MappedList, mapped_list, diff_dicts, compute_status

# Global session manager: DBSession() returns the Thread-local
# session object appropriate for the current web request.
maker = sessionmaker(autoflush=True, autocommit=False,
                     extension=ZopeTransactionExtension())
DBSession = scoped_session(maker)

# Migrate versioning
from versioning import db_init, migraterepo_get_version, db_get_version
from versioning import db_upgrade, db_downgrade

# Models import
from auth import User, Group, Permission
from misc import Taggable, Tag, Annotable, Note, Journal, Migrate
from project import Project, Scene, Shot, Libgroup, AssetContainer
from project import Category, Supervisor, Artist, Asset, AssetVersion

# Caching & helpers
from helpers import query_projects, query_projects_archived, project_get
from helpers import project_get_eager, session_get, scene_get, shot_get
from helpers import container_get, asset_get, category_get, libgroup_get
from helpers import group_get, taggable_get, tag_get, user_get
from helpers import annotable_get, note_get, assetversion_get

# Init model
def init_model(engine):
    """Call me before using any of the tables or classes in the model."""
    
    DBSession.configure(bind=engine)

