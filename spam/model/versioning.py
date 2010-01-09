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
"""Schema migration functions for SPAM database."""

from tg import config
from migrate.versioning import api as migrate_api
from migrate.versioning.exceptions import DatabaseAlreadyControlledError
from spam.model import DBSession

# DB versioning
def db_init(name, version=None):
    """Init a database and put it under ``migrate`` control."""
    db_url = config.db_url_tmpl % name
    migrate_repo = config.db_migrate_repo
    try:
        migrate_api.version_control(db_url, migrate_repo)
    except DatabaseAlreadyControlledError:
        pass
    migrate_api.upgrade(db_url, migrate_repo, version)

def migraterepo_get_version():
    """Get the ``migrate`` repository current version."""
    migrate_repo = config.db_migrate_repo
    return migrate_api.version(migrate_repo)

def db_get_version(name=None):
    """Get the ``migrate`` schema version for database ``name``."""
    sess = DBSession()
    engine = sess.bind
    result = engine.execute('SELECT version FROM migrate_version')
    version = result.fetchone()[0]
    return version

def db_upgrade(name, version=None):
    """Upgrade database ``name`` schema."""
    db_url = config.db_url_tmpl % name
    migrate_repo = config.db_migrate_repo
    migrate_api.upgrade(db_url, migrate_repo, version)
    
def db_downgrade(name, version):
    """Downgrade database ``name`` schema."""
    db_url = config.db_url_tmpl % name
    migrate_repo = config.db_migrate_repo
    migrate_api.downgrade(db_url, migrate_repo, version)
    

