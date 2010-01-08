from tg import config
from migrate.versioning import api as migrate_api
from migrate.versioning.exceptions import DatabaseAlreadyControlledError
from spam.model import DBSession

# DB versioning
def db_init(name, version=None):
    db_url = config.db_url_tmpl % name
    print('db_init:', db_url)
    migrate_repo = config.db_migrate_repo
    try:
        migrate_api.version_control(db_url, migrate_repo)
    except DatabaseAlreadyControlledError:
        pass
    migrate_api.upgrade(db_url, migrate_repo, version)

def migraterepo_get_version():
    migrate_repo = config.db_migrate_repo
    return migrate_api.version(migrate_repo)

def db_get_version(name=None):
    sess = DBSession()
    engine = sess.bind
    result = engine.execute('SELECT version FROM migrate_version')
    version = result.fetchone()[0]
    return version

def db_upgrade(name, version=None):
    db_url = config.db_url_tmpl % name
    migrate_repo = config.db_migrate_repo
    migrate_api.upgrade(db_url, migrate_repo, version)
    
def db_downgrade(name, version):
    db_url = config.db_url_tmpl % name
    migrate_repo = config.db_migrate_repo
    migrate_api.downgrade(db_url, migrate_repo, version)
    

