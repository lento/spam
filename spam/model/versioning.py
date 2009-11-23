from tg import config
from migrate.versioning import api as migrate_api
from spam.model import DBSession

# DB versioning
def db_init(proj, version=None):
    db_url = config.db_url_tmpl % proj
    migrate_repo = config.db_migrate_repo
    migrate_api.version_control(db_url, migrate_repo)
    migrate_api.upgrade(db_url, migrate_repo, version)

def migraterepo_get_version():
    migrate_repo = config.db_migrate_repo
    return migrate_api.version(migrate_repo)

def db_get_version(proj):
    sess = DBSession()
    engine = sess._ShardedSession__binds[proj]
    result = engine.execute('SELECT version FROM migrate_version')
    version = result.fetchone()[0]
    return version

def db_upgrade(proj, version=None):
    db_url = config.db_url_tmpl % proj
    migrate_repo = config.db_migrate_repo
    migrate_api.upgrade(db_url, migrate_repo, version)
    
def db_downgrade(proj, version):
    db_url = config.db_url_tmpl % proj
    migrate_repo = config.db_migrate_repo
    migrate_api.downgrade(db_url, migrate_repo, version)
    

