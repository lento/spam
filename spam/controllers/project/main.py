from tg import expose, url, tmpl_context, redirect, validate
from tg.controllers import RestController
from pylons.i18n import ugettext as _, lazy_ugettext as l_
from spam.model import session_get, Project, User, db_init, add_shard
from spam.model import project_get_eager, project_get
from spam.model import query_projects, query_projects_archived
from spam.lib.widgets import FormProjectNew, FormProjectEdit, FormProjectConfirm
from spam.lib.widgets import ProjectsActive, ProjectsArchived
from spam.lib import repo
from spam.lib.notifications import notify
from spam.lib.decorators import project_set_active

from tabs import TabController

import logging
log = logging.getLogger(__name__)

__all__ = ['ProjectsController']

# form widgets
f_new = FormProjectNew(action=url('/project/'))
f_edit = FormProjectEdit(action=url('/project/'))
f_confirm = FormProjectConfirm(action=url('/project/'))

# livetable widgets
w_projects_active = ProjectsActive()
w_projects_archived = ProjectsArchived()

class Controller(RestController):
    
    tab = TabController()
    
    @expose('spam.templates.project.get_all')
    def get_all(self):
        tmpl_context.projects_active = w_projects_active
        tmpl_context.projects_archived = w_projects_archived
        active = query_projects()
        archived = query_projects_archived()
        return dict(page='admin/project', sidebar=('admin', 'projects'),
                                            active=active, archived=archived)

    @project_set_active
    @expose('json')
    @expose('spam.templates.tabbed_content')
    def get_one(self, proj):
        project = tmpl_context.project
        tabs = [('Summary', 'tab/summary'),
                ('Scenes', url('/scene/%s' % project.id)),
                ('Tasks', 'tab/tasks'),
               ]
        return dict(page='project/%s' % project.id, tabs=tabs,
                                            sidebar=('projects', project.id))


    @expose('spam.templates.forms.form')
    def new(self, **kwargs):
        """Display a NEW form."""
        tmpl_context.form = f_new
        fargs = dict()
        fcargs = dict()
        return dict(title='Create a new project', args=fargs, child_args=fcargs)

    @expose('json')
    @expose('spam.templates.forms.result')
    @validate(f_new, error_handler=new)
    def post(self, proj, name=None, description=None, **kwargs):
        """Create a new project"""
        session = session_get()
        
        # add project to shared db
        project = Project(proj, name=name, description=description)
        session.add(project)
        
        # shards are dinamically loaded at each request, but for the current
        # request we have to add it manually
        add_shard(project.id)
        
        # init project db
        #if core_session.bind.url.drivername=='mysql':
        #    create_proj_db(project.id)
        db_init(project.id)
        
        # create directories and init hg repo
        repo.project_create_dirs(project.id)
        repo.repo_init(project.id)
        
        # grant project rights to user "admin"
        admin = session.query(User).filter_by(user_name=u'admin').one()
        project.users.append(admin)
        project.admins.append(admin)
        
        # send a stomp message to notify clients
        notify.send(project, update_type='added')
        return dict(msg='created project "%s"' % project.id, result='success')
    
    @project_set_active
    @expose('spam.templates.forms.form')
    def edit(self, proj, **kwargs):
        """Display a EDIT form."""
        tmpl_context.form = f_edit
        project = tmpl_context.project
        fargs = dict(proj=project.id, proj_d=project.id, name=project.name,
                                                description=project.description)
        fcargs = dict()
        return dict(title='Edit project "%s"' % proj, args=fargs,
                                                            child_args=fcargs)
        
    @project_set_active
    @expose('json')
    @expose('spam.templates.forms.result')
    @validate(f_edit, error_handler=edit)
    def put(self, proj, name=None, description=None, **kwargs):
        """Edit a project"""
        project = tmpl_context.project
        if name: project.name = name
        if description: project.description = description
        project.touch()
        notify.send(project, update_type='updated')
        return dict(msg='updated project "%s"' % proj, result='success')

    @project_set_active
    @expose('spam.templates.forms.form')
    def get_delete(self, proj, **kwargs):
        """Display a DELETE confirmation form."""
        tmpl_context.form = f_confirm
        project = tmpl_context.project
        fargs = dict(_method='DELETE', proj=project.id, proj_d=project.id,
                     name_d=project.name,
                     description_d=project.description,
                     create_d=project.created)
        fcargs = dict()
        warning = ('This will only delete the project entry in the database. '
                   'The data and history of the project must be deleted '
                   'manually if needed.')
        return dict(
                title='Are you sure you want to delete "%s"?' % project.name,
                warning=warning, args=fargs, child_args=fcargs)

    @project_set_active
    @expose('json')
    @expose('spam.templates.forms.result')
    @validate(f_confirm, error_handler=get_delete)
    def post_delete(self, proj, **kwargs):
        """Delete a project.
        
        Only delete the project record from the common db, the project own db
        and repository must be removed manually.
        (This should help prevent awful accidents) ;)
        """
        session = session_get()
        project = tmpl_context.project
        session.delete(project)
        notify.send(project, update_type='deleted')
        return dict(msg='deleted project "%s"' % proj, result='success')
    
    # Custom REST-like actions
    custom_actions = ['archive', 'activate', 'upgrade']
    
    @project_set_active
    @expose('spam.templates.forms.form')
    def get_archive(self, proj, **kwargs):
        """Display a ARCHIVE confirmation form."""
        tmpl_context.form = f_confirm
        project = tmpl_context.project
        fargs = dict(_method='ARCHIVE', proj=project.id, proj_d=project.id,
                     name_d=project.name,
                     description_d=project.description,
                     create_d=project.created)
        fcargs = dict()
        return dict(title='Are you sure you want to archive "%s"' % proj,
                                                args=fargs, child_args=fcargs)

    @project_set_active
    @expose('json')
    @expose('spam.templates.forms.result')
    def post_archive(self, proj, **kwargs):
        """Archive a project"""
        project = tmpl_context.project
        project.archived = True
        project.touch()
        notify.send(project, update_type='archived')
        return dict(msg='archived project "%s"' % proj, result='success')

    @expose('spam.templates.forms.form')
    def get_activate(self, proj, **kwargs):
        """Display a ACTIVATE confirmation form."""
        tmpl_context.form = f_confirm
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
        notify.send(project, update_type='activated')
        return dict(msg='activated project "%s"' % proj, result='success')

    @project_set_active
    @expose('spam.templates.forms.form')
    def get_upgrade(self, proj, **kwargs):
        """Display a UPGRADE confirmation form."""
        tmpl_context.form = f_confirm
        project = tmpl_context.project
        
        fargs = dict(_method='UPGRADE', proj=project.id, proj_d=project.id,
                     name_d=project.name,
                     description_d=project.description,
                     create_d=project.created)
        fcargs = dict()
        return dict(title='Are you sure you want to upgrade "%s" schema?' %
                                            proj, args=fargs, child_args=fcargs)

    @project_set_active
    @expose('json')
    @expose('spam.templates.forms.result')
    def post_upgrade(self, proj, **kwargs):
        """Upgrade the DB schema for a project"""
        project = tmpl_context.project
        project.schema_upgrade()
        project.touch()
        notify.send(project, update_type='updated')
        return dict(msg='upgraded project "%s" schema' % proj, result='success')


