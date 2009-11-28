"""Caching & helpers"""
from datetime import datetime
from pylons import cache
from tg import config
from sqlalchemy import create_engine
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from spam.lib.exceptions import SPAMDBError, SPAMDBNotFound
from spam.model import DBSession, Project, Scene, Shot

def add_shard(proj):
    db_url_tmpl = config.get('db_url_tmpl', 'sqlite:///spam_%s.sqlite')
    db = create_engine(db_url_tmpl % proj)
    DBSession().bind_shard(proj, db)

# Helpers
def session_get():
    shards = DBSession()._ShardedSession__binds.keys()
    for project in DBSession.query(Project):
        if project not in shards:
            add_shard(project.id)
    return DBSession()

def query_projects():
    return session_get().query(Project).filter_by(archived=False)

def query_projects_archived():
    return session_get().query(Project).filter_by(archived=True)

def project_get(proj):
    """Return a lazyloaded project"""
    try:
        return query_projects().filter_by(id=proj).one()
    except NoResultFound:
        raise SPAMDBNotFound('Project "%s" could not be found.' % proj)
    except MultipleResultsFound:
        raise SPAMDBError('Error when searching project "%s".' % proj)

def scene_get(proj, sc):
    """Return a lazyloaded scene"""
    query = session_get().query(Scene)
    try:
        return query.filter_by(proj_id=proj).filter_by(name=sc).one()
    except NoResultFound:
        raise SPAMDBNotFound('Scene "%s" could not be found.' % sc)
    except MultipleResultsFound:
        raise SPAMDBError('Error when searching scene "%s".' % sc)

def shot_get(proj, sc, sh):
    """Return a lazyloaded shot"""
    scene = scene_get(proj, sc)
    query = session_get().query(Shot).filter_by(proj_id=proj)
    try:
        return query.filter_by(parent_id=scene.id).filter_by(name=sh).one()
    except NoResultFound:
        raise SPAMDBNotFound('Shot "%s" could not be found.' % sh)
    except MultipleResultsFound:
        raise SPAMDBError('Error when searching shot "%s".' % sh)

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

def project_get_eager(proj):
    """Return a project eagerloaded with its scenes and libgroups
    
    "project_get_eager" keeps a (thread-local) cache of loaded projects,
    reloading instances from the db if the "modified" field is newer then the
    cache.
    """
    session = session_get()
    
    # get a lazyload instance of the project, save the modified time and discard
    curproject = project_get(proj)
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

