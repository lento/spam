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
"""Scene main controller"""

from tg import expose, url, tmpl_context, validate, require
from tg.controllers import RestController
from tg.decorators import with_trailing_slash
from spam.model import session_get, project_get, scene_get, Scene, diff_dicts
from spam.lib.widgets import FormSceneNew, FormSceneEdit, FormSceneConfirm
from spam.lib.widgets import TableScenes
from spam.lib import repo
from spam.lib.notifications import notify
from spam.lib.journaling import journal
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
    """REST controller for managing scenes."""
    
    tab = TabController()
    
    @project_set_active
    @require(is_project_user())
    @expose('spam.templates.scene.get_all')
    def get_all(self, proj):
        """Return a `tab` page with a list of scenes for a project and a
        button to add new scenes.
        
        This page is used as the `scenes` tab in the project view:
        :meth:`spam.controllers.project.main.get_one`.
        """
        project = tmpl_context.project
        user = tmpl_context.user
        tmpl_context.t_scenes = t_scenes
        extra_data = dict(project=project, user_id=user.user_id)
        return dict(page='scenes', sidebar=('projects', project.id),
                                scenes=project.scenes, extra_data=extra_data)

    @expose('spam.templates.scene.get_all')
    def _default(self, proj, *args, **kwargs):
        """Catch request to `scene/<something>' and pass them to :meth:`get_all`,
        because RESTController doesn't dispatch to get_all when there are
        arguments.
        """
        return self.get_all(proj)

    @project_set_active
    @require(is_project_user())
    @with_trailing_slash
    @expose('json')
    @expose('spam.templates.tabbed_content')
    def get_one(self, proj, sc):
        """Return a `tabbed` page for scene tabs."""
        scene = scene_get(proj, sc)
        
        tabs = [('Summary', 'tab/summary'),
                ('Shots', url('/shot/%s/%s/' % (scene.project.id, scene.name))),
               ]
        return dict(page='%s' % scene.path, scene=scene, tabs=tabs, 
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
    def post(self, proj, sc, description=None):
        """Create a new scene"""
        session = session_get()
        user = tmpl_context.user
        project = tmpl_context.project
        
        # add scene to db
        scene = Scene(project.id, sc, description)
        session.add(scene)
        session.flush()
        
        # create directories
        repo.scene_create_dirs(project.id, scene)
        
        # invalidate project cache
        project.touch()
        
        # log into Journal
        journal.add(user, 'created %s' % scene)
        
        # send a stomp message to notify clients
        notify.send(scene, update_type='added')
        notify.send(project)
        return dict(msg='created scene "%s"' % scene.path, result='success',
                                                                    scene=scene)
    
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
    def put(self, proj, sc, description=None):
        """Edit a scene"""
        session = session_get()
        user = tmpl_context.user
        scene = scene_get(proj, sc)
        old = scene.__dict__.copy()

        modified = False
        if description:
            scene.description = description
            modified = True
        
        if modified:
            new = scene.__dict__.copy()
        
            # log into Journal
            journal.add(user, 'modified %s: %s' % (scene, diff_dicts(old, new)))
            
            # send a stomp message to notify clients
            notify.send(scene)
            return dict(msg='updated scene "%s"' % scene.path, result='success')
        return dict(msg='scene "%s" unchanged' % scene.path, result='success')

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
    def post_delete(self, proj, sc):
        """Delete a scene.
        
        Only delete the scene record from the db, the scene directories must be
        removed manually.
        (This should help prevent awful accidents) ;)
        """
        project = tmpl_context.project
        session = session_get()
        user = tmpl_context.user
        scene = scene_get(proj, sc)
        
        if scene.shots:
            return dict(msg='cannot delete scene "%s" because it contains '
                            'shots' % scene.path,
                        result='failed')

        session.delete(scene)

        # delete association objects or they will be orphaned
        session.flush()
        session.delete(scene.taggable)
        session.delete(scene.annotable)

        # invalidate project cache
        project.touch()
        
        # log into Journal
        journal.add(user, 'deleted %s' % scene)
        
        # send a stomp message to notify clients
        notify.send(scene, update_type='deleted')
        notify.send(project)
        return dict(msg='deleted scene "%s"' % scene.path, result='success')
    
    # Custom REST-like actions
    _custom_actions = []

