# -*- coding: utf-8 -*-
#
# This file is part of SPAM (Spark Project & Asset Manager).
#
# SPAM is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# SPAM is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with SPAM.  If not, see <http://www.gnu.org/licenses/>.
#
# Original Copyright (c) 2010, Lorenzo Pierfederici <lpierfederici@gmail.com>
# Contributor(s): 
#
"""Shot main controller"""

from tg import expose, url, tmpl_context, validate, require
from tg.controllers import RestController
from tg.decorators import with_trailing_slash
from pylons.i18n import ugettext as _, lazy_ugettext as l_
from spam.model import session_get, Project, User, Shot, Tag
from spam.model import scene_get, shot_get, tag_get, diff_dicts
from spam.lib.widgets import FormShotNew, FormShotEdit, FormShotConfirm
from spam.lib.widgets import TableShots
from spam.lib import repo
from spam.lib.notifications import notify
from spam.lib.journaling import journal
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
t_shots = TableShots()

class Controller(RestController):
    """REST controller for managing shots."""
    
    tab = TabController()
    
    @project_set_active
    @require(is_project_user())
    @expose('spam.templates.shot.get_all')
    def get_all(self, proj, sc):
        """Return a `tab` page with a list of shots for a scene and a button to
        add new shots.
        
        This page is used as the `shots` tab in the scene view:
        :meth:`spam.controllers.scene.main.get_one`.
        """
        project = tmpl_context.project
        user = tmpl_context.user
        scene = scene_get(proj, sc)
        tmpl_context.scene = scene
        tmpl_context.t_shots = t_shots
        extra_data = dict(project=project, user_id=user.user_id)
        return dict(page='shot', sidebar=('projects', scene.project.id),
                                    shots=scene.shots, extra_data=extra_data)

    @expose('spam.templates.shot.get_all')
    def _default(self, proj, sc, *args, **kwargs):
        """Catch request to `shot/<something>' and pass them to :meth:`get_all`,
        because RESTController doesn't dispatch to get_all when there are
        arguments.
        """
        return self.get_all(proj, sc)

    @project_set_active
    @require(is_project_user())
    @with_trailing_slash
    @expose('json')
    @expose('spam.templates.tabbed_content')
    def get_one(self, proj, sc, sh):
        """Return a `tabbed` page for shot tabs."""
        shot = shot_get(proj, sc, sh)
        
        tabs = [('Summary', 'tab/summary'),
                ('Assets', url('/asset/%s/shot/%s' %
                                                (shot.project.id, shot.id))),
               ]
        return dict(page='%s' % shot.path, shot=shot, tabs=tabs, 
                                        sidebar=('projects', shot.project.id))

    @project_set_active
    @require(is_project_admin())
    @expose('spam.templates.forms.form2')
    def new(self, proj, sc, **kwargs):
        """Display a NEW form."""
        scene = scene_get(proj, sc)
        
        f_new.value = dict(proj=scene.project.id,
                           sc=scene.name,
                           project_name_=scene.project.name,
                           scene_name_=scene.name,
                          )
        tmpl_context.form = f_new
        return dict(title=_('Create a new shot'))

    @project_set_active
    @require(is_project_admin())
    @expose('json')
    @expose('spam.templates.forms.result')
    @validate(f_new, error_handler=new)
    def post(self, proj, sc, sh, description=None, action=None, frames=None,
                                            handle_in=None, handle_out=None):
        """Create a new shot"""
        project = tmpl_context.project
        session = session_get()
        user = tmpl_context.user
        scene = scene_get(proj, sc)
        
        # add shot to db
        shot = Shot(scene, sh, description=description, action=action,
                    frames=frames, handle_in=handle_in, handle_out=handle_out)
        session.add(shot)
        session.flush()
        
        # create directories
        repo.shot_create_dirs(scene.project.id, shot)
        
        # invalidate project cache
        project.touch()
        
        # log into Journal
        journal.add(user, 'created %s' % shot)
        
        # send a stomp message to notify clients
        notify.send(shot, update_type='added')
        notify.send(project)
        return dict(msg='created shot "%s"' % shot.path, result='success',
                                                                    shot=shot)
    
    @project_set_active
    @require(is_project_admin())
    @expose('spam.templates.forms.form2')
    def edit(self, proj, sc, sh, **kwargs):
        """Display a EDIT form."""
        shot = shot_get(proj, sc, sh)
        
        f_edit.value = dict(proj=shot.project.id,
                            sc=shot.parent.name,
                            sh=shot.name,
                            project_name_=shot.project.name,
                            scene_name_=shot.parent.name,
                            shot_name_=shot.name,
                            description=shot.description,
                            action=shot.action,
                            frames=shot.frames,
                            handle_in=shot.handle_in,
                            handle_out=shot.handle_out,
                           )
        tmpl_context.form = f_edit
        return dict(title='%s %s' % (_('Edit shot'), shot.path))
        
    @project_set_active
    @require(is_project_admin())
    @expose('json')
    @expose('spam.templates.forms.result')
    @validate(f_edit, error_handler=edit)
    def put(self, proj, sc, sh, description=None, action=None, frames=None,
                                            handle_in=None, handle_out=None):
        """Edit a shot"""
        session = session_get()
        user = tmpl_context.user
        shot = shot_get(proj, sc, sh)
        old = shot.__dict__.copy()
        
        modified = False
        if description:
            shot.description = description
            modified = True
        
        if action:
            shot.action = action
            modified = True
        
        if frames:
            shot.frames = frames
            modified = True
        
        if handle_in:
            shot.handle_in = handle_in
            modified = True
        
        if handle_out:
            shot.handle_out = handle_out
            modified = True
        
        if modified:
            new = shot.__dict__.copy()
        
            # log into Journal
            journal.add(user, 'modified %s: %s' % (shot, diff_dicts(old, new)))
            
            # send a stomp message to notify clients
            notify.send(shot)
            return dict(msg='updated shot "%s"' % shot.path, result='success')
        return dict(msg='shot "%s" unchanged' % shot.path, result='success')

    @project_set_active
    @require(is_project_admin())
    @expose('spam.templates.forms.form2')
    def get_delete(self, proj, sc, sh, **kwargs):
        """Display a DELETE confirmation form."""
        shot = shot_get(proj, sc, sh)
        f_confirm.custom_method = 'DELETE'
        f_confirm.value = dict(proj=shot.project.id,
                               sc=shot.parent.name,
                               sh=shot.name,
                               project_name_=shot.project.name,
                               scene_name_=shot.parent.name,
                               shot_name_=shot.name,
                               description_=shot.description,
                              )
        warning = ('This will only delete the shot entry in the database. '
                   'The data must be deleted manually if needed.')
        tmpl_context.form = f_confirm
        return dict(title='%s %s?' % (_('Are you sure you want to delete'),
                                                    shot.path), warning=warning)

    @project_set_active
    @require(is_project_admin())
    @expose('json')
    @expose('spam.templates.forms.result')
    @validate(f_confirm, error_handler=get_delete)
    def post_delete(self, proj, sc, sh):
        """Delete a shot.
        
        Only delete the shot record from the db, the shot directories must be
        removed manually.
        (This should help prevent awful accidents) ;)
        """
        project = tmpl_context.project
        session = session_get()
        user = tmpl_context.user
        shot = shot_get(proj, sc, sh)
        
        if shot.assets:
            return dict(msg='cannot delete shot "%s" because it contains '
                            'assets' % shot.path,
                        result='failed')

        session.delete(shot)

        # delete association objects or they will be orphaned
        session.flush()
        session.delete(shot.container)
        session.delete(shot.taggable)
        session.delete(shot.annotable)

        # invalidate project cache
        project.touch()
        
        
        # log into Journal
        journal.add(user, 'deleted %s' % shot)
        
        # send a stomp message to notify clients
        notify.send(shot, update_type='deleted')
        notify.send(project)
        return dict(msg='deleted shot "%s"' % shot.path, result='success')
    
    # Custom REST-like actions
    _custom_actions = []

