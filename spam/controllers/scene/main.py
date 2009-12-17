from tg import expose, url, tmpl_context, validate, require
from tg.controllers import RestController
from tg.decorators import with_trailing_slash
from spam.model import session_get, Scene
from spam.model import project_get, scene_get
from spam.lib.widgets import FormSceneNew, FormSceneEdit, FormSceneConfirm
from spam.lib.widgets import TableScenes
from spam.lib import repo
from spam.lib.notifications import notify
from spam.lib.decorators import project_set_active
from spam.lib.predicates import is_project_user, is_project_admin

from tabs import TabController

import logging
log = logging.getLogger(__name__)

# form widgets
f_new = FormSceneNew(action=url('/scene/'))
f_edit = FormSceneEdit(action=url('/scene/'))
f_confirm = FormSceneConfirm(action=url('/scene/'))

# livetable widgets
t_scenes = TableScenes()

class Controller(RestController):
    
    tab = TabController()
    
    @project_set_active
    @require(is_project_user())
    @expose('spam.templates.project.tabs.scenes')
    def get_all(self, proj):
        project = tmpl_context.project
        tmpl_context.t_scenes = t_scenes
        return dict(page='scenes', sidebar=('projects', project.id),
                                                        scenes=project.scenes)

    @expose('spam.templates.project.tabs.scenes')
    def default(self, proj, *args, **kwargs):
        return self.get_all(proj)

    @project_set_active
    @require(is_project_user())
    @with_trailing_slash
    @expose('json')
    @expose('spam.templates.tabbed_content')
    def get_one(self, proj, sc):
        scene = scene_get(proj, sc)
        
        tabs = [('Summary', 'tab/summary'),
                ('Shots', url('/shot/%s/%s/' % (scene.project.id, scene.name))),
               ]
        return dict(page='%s' % scene.path, tabs=tabs, 
                                        sidebar=('projects', scene.project.id))

    @project_set_active
    @require(is_project_admin())
    @expose('spam.templates.forms.form')
    def new(self, proj, **kwargs):
        """Display a NEW form."""
        tmpl_context.form = f_new
        project = tmpl_context.project

        fargs = dict(proj=project.id, project_=project.name)
        fcargs = dict()
        return dict(title='Create a new scene', args=fargs, child_args=fcargs)

    @project_set_active
    @require(is_project_admin())
    @expose('json')
    @expose('spam.templates.forms.result')
    @validate(f_new, error_handler=new)
    def post(self, proj, sc, description=None, **kwargs):
        """Create a new scene"""
        session = session_get()
        project = tmpl_context.project
        
        # add scene to db
        scene = Scene(project.id, sc, description)
        session.add(scene)
        session.flush()
        
        # create directories
        repo.scene_create_dirs(project.id, scene)
        
        # invalidate project cache
        project.touch()
        
        # send a stomp message to notify clients
        notify.send(scene, update_type='added')
        notify.send(project)
        return dict(msg='created scene "%s"' % scene.path, result='success')
    
    @project_set_active
    @require(is_project_admin())
    @expose('spam.templates.forms.form')
    def edit(self, proj, sc, **kwargs):
        """Display a EDIT form."""
        tmpl_context.form = f_edit
        scene = scene_get(proj, sc)

        fargs = dict(proj=scene.project.id, project_=scene.project.name,
                     sc=scene.name, name_=scene.name,
                     description=scene.description)
        fcargs = dict()
        return dict(title='Edit scene "%s"' % scene.path,
                                                args=fargs, child_args=fcargs)
        
    @project_set_active
    @require(is_project_admin())
    @expose('json')
    @expose('spam.templates.forms.result')
    @validate(f_edit, error_handler=edit)
    def put(self, proj, sc, description=None, **kwargs):
        """Edit a scene"""
        scene = scene_get(proj, sc)

        if description: scene.description = description
        notify.send(scene)
        return dict(msg='updated scene "%s"' % scene.path, result='success')

    @project_set_active
    @require(is_project_admin())
    @expose('spam.templates.forms.form')
    def get_delete(self, proj, sc, **kwargs):
        """Display a DELETE confirmation form."""
        tmpl_context.form = f_confirm
        scene = scene_get(proj, sc)

        fargs = dict(_method='DELETE',
                     proj=scene.project.id, project_=scene.project.name,
                     sc=scene.name, name_=scene.name,
                     description_=scene.description)
        fcargs = dict()
        warning = ('This will only delete the scene entry in the database. '
                   'The data must be deleted manually if needed.')
        return dict(
                title='Are you sure you want to delete "%s"?' % scene.path,
                warning=warning, args=fargs, child_args=fcargs)

    @project_set_active
    @require(is_project_admin())
    @expose('json')
    @expose('spam.templates.forms.result')
    @validate(f_confirm, error_handler=get_delete)
    def post_delete(self, proj, sc, **kwargs):
        """Delete a scene.
        
        Only delete the scene record from the db, the scene directories must be
        removed manually.
        (This should help prevent awful accidents) ;)
        """
        project = tmpl_context.project
        session = session_get()
        scene = scene_get(proj, sc)
        if scene.shots:
            return dict(msg='cannot delete scene "%s" because it contains '
                            'shots' % scene.path,
                        result='failed')
        
        session.delete(scene)

        # invalidate project cache
        project.touch()
        
        notify.send(scene, update_type='deleted')
        notify.send(project)
        return dict(msg='deleted scene "%s"' % scene.path, result='success')
    
    # Custom REST-like actions
    custom_actions = []

