import logging, datetime
from pylons import cache
from tg import expose, url, tmpl_context, redirect, validate
from tg.controllers import RestController
from spam.model import get_session, Project, User,  db_init
from spam.model import get_project_eager, get_project_lazy
from spam.model import query_projects, query_projects_archived
from spam.lib.widgets import FormProjectNew, FormProjectEdit, FormProjectConfirm
from spam.lib.widgets import ProjectsActive, ProjectsArchived
from spam.lib import repo

__all__ = ['ProjectsController']
log = logging.getLogger(__name__)

# form widgets
f_project_new = FormProjectNew(action=url('/project/'))
f_project_edit = FormProjectEdit(action=url('/project/'))
f_project_delete = FormProjectConfirm(action=url('/project/'))
f_project_confirm = FormProjectConfirm(action=url('/project/'))

# livetable widgets
w_projects_active = ProjectsActive()
w_projects_archived = ProjectsArchived()

class ProjectController(RestController):
    
    @expose('spam.templates.project.get_all')
    def get_all(self):
        tmpl_context.projects_active = w_projects_active
        tmpl_context.projects_archived = w_projects_archived
        active = query_projects()
        archived = query_projects_archived()
        return dict(page='admin/projects', sidebar=('admin', 'projects'),
                                            active=active, archived=archived)

    @expose('json')
    @expose('spam.templates.project.get_one')
    def get_one(self, proj):
        project = get_project_eager(proj)
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
        session = get_session()
        
        # add project to shared db
        project = Project(proj, name=name, description=description)
        session.add(project)
        
        # init project db
        #if core_session.bind.url.drivername=='mysql':
        #    create_proj_db(project.id)
        db_init(project.id)
        
        # create directories and init hg repo
        repo.create_proj_dirs(project.id)
        repo.init_repo(project.id)
        
        # grant project rights to user "admin"
        admin = session.query(User).filter_by(user_name=u'admin').one()
        project.users.append(admin)
        project.admins.append(admin)
        
        return dict(msg='created project "%s"' % project.id, result='success')
    
    @expose('spam.templates.forms.form')
    def edit(self, proj, **kwargs):
        """Display a EDIT form."""
        tmpl_context.form = f_project_edit
        project = get_project_lazy(proj)
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
        project = get_project_lazy(proj)
        if name: project.name = name
        if description: project.description = description
        project.touch()
        return dict(msg='updated project "%s"' % proj, result='success')

    @expose('spam.templates.forms.form')
    def get_delete(self, proj, **kwargs):
        """Display a DELETE confirmation form."""
        tmpl_context.form = f_project_delete
        project = get_project_lazy(proj)
        fargs = dict(_method='DELETE', proj=project.id, proj_d=project.id,
                     name_d=project.name,
                     description_d=project.description,
                     create_d=project.created)
        fcargs = dict()
        warning = ('This will only delete the project registration in the '
                   'database. The data and history of the project must be '
                   'deleted manually if needed.')
        return dict(
                title='Are you sure you want to delete "%s"?' % project.name,
                warning=warning, args=fargs, child_args=fcargs)

    @expose('json')
    @expose('spam.templates.forms.result')
    @validate(f_project_delete, error_handler=get_delete)
    def post_delete(self, proj, **kwargs):
        """Delete a project.
        
        Only delete the project record from the common db, the project own db
        and repository must be removed manually.
        (This should help prevent awful accidents) ;)
        """
        session = get_session()
        project = get_project_lazy(proj)
        session.delete(project)
        return dict(msg='deleted project "%s"' % proj, result='success')
    
    # Custom REST-like actions
    custom_actions = ['archive', 'activate', 'upgrade']
    
    @expose('spam.templates.forms.form')
    def get_archive(self, proj, **kwargs):
        """Display a ARCHIVE confirmation form."""
        tmpl_context.form = f_project_confirm
        project = get_project_lazy(proj)
        fargs = dict(_method='ARCHIVE', proj=project.id, proj_d=project.id,
                     name_d=project.name,
                     description_d=project.description,
                     create_d=project.created)
        fcargs = dict()
        return dict(title='Are you sure you want to archive "%s"' % proj,
                                                args=fargs, child_args=fcargs)

    @expose('json')
    @expose('spam.templates.forms.result')
    def post_archive(self, proj, **kwargs):
        """Archive a project"""
        project = get_project_lazy(proj)
        project.archived = True
        project.touch()
        return dict(msg='archived project "%s"' % proj, result='success')

    @expose('spam.templates.forms.form')
    def get_activate(self, proj, **kwargs):
        """Display a ACTIVATE confirmation form."""
        tmpl_context.form = f_project_confirm
        project = query_projects_archived().filter_by(id=proj).one()
        log.debug('get_activate: %s' % project)
        
        fargs = dict(_method='ACTIVATE', proj=project.id, proj_d=project.id,
                     name_d=project.name,
                     description_d=project.description,
                     create_d=project.created)
        fcargs = dict()
        return dict(title='Are you sure you want to activate "%s"' % proj,
                                                args=fargs, child_args=fcargs)

    @expose('json')
    @expose('spam.templates.forms.result')
    def post_activate(self, proj, **kwargs):
        """Activate a project"""
        project = query_projects_archived().filter_by(id=proj).one()
        project.archived = False
        project.touch()
        return dict(msg='activated project "%s"' % proj, result='success')

    @expose('spam.templates.forms.form')
    def get_upgrade(self, proj, **kwargs):
        """Display a UPGRADE confirmation form."""
        tmpl_context.form = f_project_confirm
        project = get_project_lazy(proj)
        
        fargs = dict(_method='UPGRADE', proj=project.id, proj_d=project.id,
                     name_d=project.name,
                     description_d=project.description,
                     create_d=project.created)
        fcargs = dict()
        return dict(title='Are you sure you want to upgrade "%s" schema?' %
                                            proj, args=fargs, child_args=fcargs)

    @expose('json')
    @expose('spam.templates.forms.result')
    def post_upgrade(self, proj, **kwargs):
        """Upgrade the DB schema for a project"""
        project = get_project_lazy(proj)
        project.schema_upgrade()
        project.touch()
        return dict(msg='upgraded project "%s" schema' % proj, result='success')


