from pylons import cache
from tg import expose, url, tmpl_context, redirect, validate
from tg.controllers import RestController
from spam.model import DBSession, Project
from spam.lib.widgets import FormNewProject, FormEditProject
from spam.lib.widgets import ActiveProjects, ArchivedProjects

__all__ = ['ProjectsController']

# form widgets
f_new_project = FormNewProject(action=url('/admin/projects/'))
f_edit_project = FormEditProject(action=url('/admin/projects/'))

# livetable widgets
w_active_projects = ActiveProjects()
w_archived_projects = ArchivedProjects()

class ProjectsController(RestController):

    @expose('spam.templates.admin.projects.get_all')
    def get_all(self):
        tmpl_context.active_projects = w_active_projects
        tmpl_context.archived_projects = w_archived_projects
        active = DBSession.query(Project).all()
        archived = [active[0]]*5
        return dict(page='admin/projects', sidebar=('admin', 'projects'),
                                            active=active, archived=archived)

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
    
    #@expose('spam.templates.forms.form')
    #def edit(self, *args, **kwargs):
    #    tmpl_context.form = f_edit_project
    #    fargs = dict()
    #    fcargs = dict()
    #    return dict(title='Edit project "%s - %s"' % (args, kwargs), args=fargs,
    #                                                        child_args=fcargs)
        
    @expose('spam.templates.forms.form')
    def get_one(self, proj, num):
        tmpl_context.form = f_edit_project
        fargs = dict()
        fcargs = dict()
        return dict(title='Get project "%s - %s"' % (proj, num), args=fargs,
                                                            child_args=fcargs)

