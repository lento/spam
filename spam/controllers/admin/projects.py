from pylons import cache
from tg import expose, url, tmpl_context, redirect, validate
from tg.controllers import RestController
from spam.model import DBSession, Project
from spam.lib.widgets import FormNewProject

__all__ = ['ProjectsController']

f_new_project = FormNewProject(action=url('/admin/projects/'))


class ProjectsController(RestController):

    @expose('spam.templates.admin.projects.get_all')
    def get_all(self):
        projects = DBSession.query(Project).all()
        return dict(page='admin/projects', sidebar=('admin', 'projects'),
                                                            projects=projects)

    @expose('spam.templates.forms.form')
    def new(self, **kwargs):
        tmpl_context.form = f_new_project
        fargs = dict()
        fcargs = dict()
        return dict(title='Create a new project', args=fargs, child_args=fcargs)

    @expose('spam.templates.forms.result')
    @expose('json')
    @validate(f_new_project, error_handler=new)
    def post(self, id, name=None, description=None, **kwargs):
        """Create a new project"""
        # add project to shared db
        #project = Project(id, name=name, description=description)
        #DBSession.add(project)
        
        # init project db
        #if core_session.bind.url.drivername=='mysql':
        #    create_proj_db(project.id)
        #init_proj_db(project.id)
        
        # create directories and init hg repo
        #repo.create_proj_dirs(project.id)
        return dict(msg='created project "%s"' % id, result='success')
    
    @expose()
    def invalidate_cache(self, proj):
        projcache = cache.get_cache('projects')
        projcache.remove_value(proj)
        return 'removed'

