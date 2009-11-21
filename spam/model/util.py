"""Caching & helpers"""
from datetime import datetime
from migrate.versioning import api as migrate_api
from pylons import cache
from tg import config
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from spam.lib.exceptions import SPAMProjectNotFound
from spam.model import DBSession, Project

def query_projects():
    return DBSession.query(Project).filter_by(archived=False)

def query_projects_archived():
    return DBSession.query(Project).filter_by(archived=True)

# Cache
def eagerload_maker(proj):
    """Factory for project eagerloaders.
    
    Return a argument-less function suitable for the "createfunc" parameter of
    "Cache.get_value"
    """
    def eagerload_project():
        try:
            project = query_projects().filter_by(id=proj).one()
        except (NoResultFound, MultipleResultsFound):
            raise SPAMProjectNotFound('Project "%s" could not be found.' % proj)
        project.scenes
        project.libgroups
        return (project, datetime.now())
    return eagerload_project

def get_project(proj):
    """Return a project eagerloaded with its scenes and libgroups
    
    "get_project" keeps a (thread-local) cache of loaded projects, reloading
    instances from the db if the "modified" field is newer then the cache
    """
    # get a lazyload instance of the project, save the modified time and discard
    try:
        curproject = query_projects().filter_by(id=proj).one()
    except (NoResultFound, MultipleResultsFound):
        raise SPAMProjectNotFound('Project "%s" could not be found.' % proj)
    modified = curproject.modified
    DBSession.expunge(curproject)
    
    # get the project from cache
    projcache = cache.get_cache('projects')
    project, cached = projcache.get_value(key=proj,
                                  createfunc=eagerload_maker(proj),
                                  expiretime=360)

    # check if its older then the db
    if cached < modified:
        # remove the invalidated value from the cache and reload from db
        projcache.remove_value(proj)
        project, cached = projcache.get_value(key=proj,
                                  createfunc=eagerload_maker(proj),
                                  expiretime=360)
    
    # put the instance back into the session
    if project not in DBSession:
        DBSession.add(project)
    
    return project

# DB versioning
def init_db(proj, version=None):
    db_url = config.db_url_tmpl % proj
    migrate_repo = config.db_migrate_repo
    migrate_api.version_control(db_url, migrate_repo)
    migrate_api.upgrade(db_url, migrate_repo, version)

