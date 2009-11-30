from tg import expose, url, tmpl_context, validate, require
from tg.controllers import RestController
from spam.model import session_get, Project, User, Shot
from spam.model import scene_get, shot_get
from spam.lib.widgets import FormShotNew, FormShotEdit, FormShotConfirm
from spam.lib import repo
from spam.lib.notifications import notify
from spam.lib.decorators import project_set_active
from spam.lib.predicates import is_project_user, is_project_admin

from tabs import TabController

import logging
log = logging.getLogger(__name__)

# form widgets
f_new = FormShotNew(action=url('/shot/'))
f_edit = FormShotEdit(action=url('/shot/'))
f_confirm = FormShotConfirm(action=url('/shot/'))

# livetable widgets

class Controller(RestController):
    
    tab = TabController()
    
    @project_set_active
    @require(is_project_user())
    @expose('spam.templates.scene.tabs.shots')
    def get_all(self, proj, sc):
        scene = scene_get(proj, sc)
        tmpl_context.scene = scene
        return dict(page='shot', sidebar=('projects', scene.project.id),
                                                            shots=scene.shots)

    @expose('spam.templates.scene.tabs.shots')
    def default(self, proj, sc, *args, **kwargs):
        return self.get_all(proj, sc)

    @project_set_active
    @require(is_project_user())
    @expose('json')
    @expose('spam.templates.tabbed_content')
    def get_one(self, proj, sc, sh):
        shot = shot_get(proj, sc, sh)
        
        tabs = [('Summary', 'tab/summary'),
                ('Assets', 'tab/assets'),
                ('Tasks', 'tab/tasks'),
               ]
        return dict(page='%s' % shot.path, tabs=tabs, 
                                        sidebar=('projects', shot.project.id))

    @project_set_active
    @require(is_project_admin())
    @expose('spam.templates.forms.form')
    def new(self, proj, sc, **kwargs):
        """Display a NEW form."""
        tmpl_context.form = f_new
        scene = scene_get(proj, sc)
        
        fargs = dict(proj=scene.project.id, _project=scene.project.name,
                     sc=scene.name, _scene=scene.name)
        fcargs = dict()
        return dict(title='Create a new shot', args=fargs, child_args=fcargs)

    @project_set_active
    @require(is_project_admin())
    @expose('json')
    @expose('spam.templates.forms.result')
    @validate(f_new, error_handler=new)
    def post(self, proj, sc, sh, description=None, action=None, frames=0,
             handle_in=0, handle_out=0, **kwargs):
        """Create a new shot"""
        session = session_get()
        scene = scene_get(proj, sc)
        
        # add shot to db
        shot = Shot(scene.project.id, sh, parent=scene, description=description,
                    action=action, frames=frames, handle_in=handle_in,
                    handle_out=handle_out)
        session.add(shot)
        session.flush()
        
        # create directories
        repo.shot_create_dirs(scene.project.id, scene.name, shot.name)
        
        # send a stomp message to notify clients
        notify.send(shot, update_type='added')
        return dict(msg='created shot "%s"' % shot.path, result='success')
    
    @project_set_active
    @require(is_project_admin())
    @expose('spam.templates.forms.form')
    def edit(self, proj, sc, sh, **kwargs):
        """Display a EDIT form."""
        tmpl_context.form = f_edit
        shot = shot_get(proj, sc, sh)
        
        fargs = dict(proj=shot.project.id, _project=shot.project.name,
                     sc=shot.parent.name, _scene=shot.parent.name,
                     sh=shot.name, _name=shot.name,
                     description=shot.description, action=shot.action,
                     frames=shot.frames, handle_in=shot.handle_in,
                     handle_out=shot.handle_out)
        fcargs = dict()
        return dict(title='Edit shot "%s"' % shot.path, args=fargs,
                                                            child_args=fcargs)
        
    @project_set_active
    @require(is_project_admin())
    @expose('json')
    @expose('spam.templates.forms.result')
    @validate(f_edit, error_handler=edit)
    def put(self, proj, sc, sh, description=None, action=None,
                  frames=0, handle_in=0, handle_out=0, **kwargs):
        """Edit a shot"""
        shot = shot_get(proj, sc, sh)
        
        if description: shot.description = description
        if action: shot.action = action
        if frames: shot.frames = frames
        if handle_in: shot.handle_in = handle_in
        if handle_out: shot.handle_out = handle_out
        
        notify.send(shot)
        return dict(msg='updated shot "%s"' % shot.path, result='success')

    @project_set_active
    @require(is_project_admin())
    @expose('spam.templates.forms.form')
    def get_delete(self, proj, sc, sh, **kwargs):
        """Display a DELETE confirmation form."""
        tmpl_context.form = f_confirm
        shot = shot_get(proj, sc, sh)
        fargs = dict(_method='DELETE',
                     proj=shot.project.id, _project=shot.project.name,
                     sc=shot.parent.name, _scene=shot.parent.name,
                     sh=shot.name, _name=shot.name,
                     _description=shot.description, _action=shot.action,
                     _frames=shot.frames, _handle_in=shot.handle_in,
                     _handle_out=shot.handle_out)
        fcargs = dict()
        warning = ('This will only delete the shot entry in the database. '
                   'The data must be deleted manually if needed.')
        return dict(
                title='Are you sure you want to delete "%s"?' % shot.path,
                warning=warning, args=fargs, child_args=fcargs)

    @project_set_active
    @require(is_project_admin())
    @expose('json')
    @expose('spam.templates.forms.result')
    @validate(f_confirm, error_handler=get_delete)
    def post_delete(self, proj, sc, sh, **kwargs):
        """Delete a shot.
        
        Only delete the shot record from the db, the shot directories must be
        removed manually.
        (This should help prevent awful accidents) ;)
        """
        session = session_get()
        shot = shot_get(proj, sc, sh)
        
        session.delete(shot)
        notify.send(shot, update_type='removed')
        return dict(msg='deleted shot "%s"' % shot.path, result='success')
    
    # Custom REST-like actions
    custom_actions = []

