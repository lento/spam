"""Caching & helpers"""
from datetime import datetime
from pylons import cache
from tg import config
from sqlalchemy import create_engine
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from spam.lib.exceptions import SPAMProjectNotFound
from spam.model import DBSession, Project

def add_shard(proj):
    db_url_tmpl = config.get('db_url_tmpl', 'sqlite:///spam_%s.sqlite')
    db = create_engine(db_url_tmpl % proj)
    DBSession().bind_shard(proj, db)

def get_session():
    shards = DBSession()._ShardedSession__binds.keys()
    for project in DBSession.query(Project):
        if project not in shards:
            add_shard(project.id)
    return DBSession()

def query_projects():
    return get_session().query(Project).filter_by(archived=False)

def query_projects_archived():
    return get_session().query(Project).filter_by(archived=True)

# Cache
def get_project_lazy(proj):
    """Return a lazyloaded project"""
    try:
        return query_projects().filter_by(id=proj).one()
    except (NoResultFound, MultipleResultsFound):
        raise SPAMProjectNotFound('Project "%s" could not be found.' % proj)

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

def get_project_eager(proj):
    """Return a project eagerloaded with its scenes and libgroups
    
    "get_project_eager" keeps a (thread-local) cache of loaded projects,
    reloading instances from the db if the "modified" field is newer then the
    cache.
    """
    session = get_session()
    
    # get a lazyload instance of the project, save the modified time and discard
    curproject = get_project_lazy(proj)
    modified = curproject.modified
    session.expunge(curproject)
    
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
    if project not in session:
        session.add(project)
    
    return project

