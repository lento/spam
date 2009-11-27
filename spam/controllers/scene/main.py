from tg import expose, url, tmpl_context, redirect, validate
from tg.controllers import RestController
from spam.model import get_session, Project, User
from spam.model import get_project_eager, get_project_lazy
from spam.model import query_projects, query_projects_archived
from spam.lib.widgets import FormSceneNew, FormSceneEdit, FormSceneConfirm
from spam.lib import repo, notify

from tabs import TabController

import logging
log = logging.getLogger(__name__)

# form widgets
f_new = FormSceneNew(action=url('/project/'))
f_edit = FormSceneEdit(action=url('/project/'))
f_confirm = FormSceneConfirm(action=url('/project/'))

# livetable widgets

class Controller(RestController):
    
    tab = TabController()
    
    @expose('spam.templates.scene.get_all')
    def get_all(self, proj):
        project = get_project_eager(proj)
        return dict(page='scenes', sidebar=('projects', project.id),
                                                        scenes=project.scenes)

    @expose('spam.templates.scene.get_all')
    def default(self, proj, *args, **kwargs):
        return self.get_all(proj)

    @expose('json')
    @expose('spam.templates.tabs')
    def get_one(self, proj, sc):
        # we add the project to tmpl_context to show the project sidebar
        project = get_project_eager(proj)
        tmpl_context.project = project
        
        scene = [s for s in project.scenes if s.name==sc][0]
        tabs = [('Summary', 'tab/summary'),
                ('Shots', url('/shot/%s/%s' % (project.id, scene.name))),
                ('Tasks', 'tab/tasks'),
               ]
        return dict(page='scenes/%s' % scene.name, tabs=tabs, 
                                            sidebar=('projects', project.id))

    @expose('spam.templates.forms.form')
    def new(self, proj, **kwargs):
        tmpl_context.form = f_new
        fargs = dict()
        fcargs = dict()
        return dict(title='Create a new scene', args=fargs, child_args=fcargs)

    @expose('json')
    @expose('spam.templates.forms.result')
    @validate(f_new, error_handler=new)
    def post(self, proj, name=None, description=None, **kwargs):
        """Create a new scene"""
        session = get_session()
        
        # add scene to db
        
        # create directories
        
        # send a stomp message to notify clients
        return dict(msg='created scene "%s"' % 'scena', result='success')
    
    @expose('spam.templates.forms.form')
    def edit(self, proj, sc, **kwargs):
        """Display a EDIT form."""
        tmpl_context.form = f_edit
        fargs = dict()
        fcargs = dict()
        return dict(title='Edit scene "%s"' % 'scena', args=fargs,
                                                            child_args=fcargs)
        
    @expose('json')
    @expose('spam.templates.forms.result')
    @validate(f_edit, error_handler=edit)
    def put(self, proj, sc, name=None, description=None, **kwargs):
        """Edit a scene"""
        return dict(msg='updated scene "%s"' % 'scena', result='success')

    @expose('spam.templates.forms.form')
    def get_delete(self, proj, sc, **kwargs):
        """Display a DELETE confirmation form."""
        tmpl_context.form = f_delete
        fargs = dict()
        fcargs = dict()
        warning = ('This will only delete the scene registration in the '
                   'database. The data must be deleted manually if needed.')
        return dict(
                title='Are you sure you want to delete "%s"?' % 'scena',
                warning=warning, args=fargs, child_args=fcargs)

    @expose('json')
    @expose('spam.templates.forms.result')
    @validate(f_confirm, error_handler=get_delete)
    def post_delete(self, proj, sc, **kwargs):
        """Delete a scene.
        
        Only delete the scene record from the db, the scene directories must be
        removed manually.
        (This should help prevent awful accidents) ;)
        """
        return dict(msg='deleted scene "%s"' % 'scena', result='success')
    
    # Custom REST-like actions
    custom_actions = []

