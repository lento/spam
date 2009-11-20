from pylons import cache
from tg import expose, url, tmpl_context, redirect, validate
from tg.controllers import RestController
from spam.model import DBSession, Project, get_project
from spam.lib.widgets import FormProjectNew, FormProjectEdit, FormProjectDelete
from spam.lib.widgets import ProjectsActive, ProjectsArchived

__all__ = ['ProjectsController']

# form widgets
f_project_new = FormProjectNew(action=url('/project/'))
f_project_edit = FormProjectEdit(action=url('/project/'))
f_project_delete = FormProjectDelete(action=url('/project/'))

# livetable widgets
w_projects_active = ProjectsActive()
w_projects_archived = ProjectsArchived()

class ProjectController(RestController):

    @expose('spam.templates.project.get_all')
    def get_all(self):
        tmpl_context.projects_active = w_projects_active
        tmpl_context.projects_archived = w_projects_archived
        active = DBSession.query(Project).all()
        archived = [active[0]]*5
        return dict(page='admin/projects', sidebar=('admin', 'projects'),
                                            active=active, archived=archived)

    @expose('json')
    @expose('spam.templates.project.get_one')
    def get_one(self, proj):
        project = get_project(proj)
        return dict(page='admin/projects/%s' % proj, project=project,
                                                sidebar=('projects', project.id))


    @expose('spam.templates.forms.form')
    def new(self, **kwargs):
        tmpl_context.form = f_project_new
        fargs = dict()
        fcargs = dict()
        return dict(title='Create a new project', args=fargs, child_args=fcargs)

    @expose('json')
    @expose('spam.templates.forms.result')
    @validate(f_project_new, error_handler=new)
    def post(self, proj, name=None, description=None, **kwargs):
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
        return dict(msg='created project "%s"' % proj, result='success')
    
    @expose('spam.templates.forms.form')
    def edit(self, proj, **kwargs):
        """Display a EDIT confirmation form."""
        tmpl_context.form = f_project_edit
        project = get_project(proj)
        fargs = dict(proj=project.id, proj_d=project.id, name=project.name,
                                                description=project.description)
        fcargs = dict()
        return dict(title='Edit project "%s"' % proj, args=fargs,
                                                            child_args=fcargs)
        
    @expose('json')
    @expose('spam.templates.forms.result')
    @validate(f_project_edit, error_handler=edit)
    def put(self, proj, name=None, description=None, **kwargs):
        """Edit a project"""
        project = get_project(proj)
        if name: project.name = name
        if description: project.description = description
        return dict(msg='updated project "%s"' % proj, result='success')

    @expose('spam.templates.forms.form')
    def get_delete(self, proj, **kwargs):
        """Display a DELETE confirmation form."""
        tmpl_context.form = f_project_delete
        project = get_project(proj)
        fargs = dict(proj=project.id, proj_d=project.id,
                     name_d=project.name,
                     description_d=project.description,
                     create_d=project.created)
        fcargs = dict()
        warning = ('All the data and history of the project will be lost, '
                   'this action is not undoable!')
        return dict(
                title='Are you sure you want to delete "%s"?' % project.name,
                warning=warning, args=fargs, child_args=fcargs)

    @expose('json')
    @expose('spam.templates.forms.result')
    @validate(f_project_delete, error_handler=get_delete)
    def post_delete(self, proj, **kwargs):
        """Delete a project"""
        project = get_project(proj)
        #DBSession.delete(project)
        return dict(msg='deleted project "%s"' % proj, result='success')

