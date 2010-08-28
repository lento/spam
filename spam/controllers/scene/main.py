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
from pylons.i18n import ugettext as _, lazy_ugettext as l_
from spam.model import session_get, project_get, scene_get, Scene, diff_dicts
from spam.lib.widgets import FormSceneNew, FormSceneEdit, FormSceneConfirm
from spam.lib.widgets import TableScenes
from spam.lib import repo
from spam.lib.notifications import notify, TOPIC_SCENES
from spam.lib.notifications import TOPIC_PROJECT_STRUCTURE
from spam.lib.journaling import journal
from spam.lib.decorators import project_set_active
from spam.lib.predicates import is_project_user, is_project_admin

from tabs import TabController

import logging
log = logging.getLogger(__name__)

# form widgets
f_new = FormSceneNew(action=url('/scene'))
f_edit = FormSceneEdit(action=url('/scene'))
f_confirm = FormSceneConfirm(action=url('/scene'))

# livetable widgets
t_scenes = TableScenes(id='t_scenes')

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

        t_scenes.value = project.scenes
        t_scenes.extra_data = dict(project=project, user_id=user.user_id)
        tmpl_context.t_scenes = t_scenes
        return dict(page='scenes', sidebar=('projects', project.id))

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
        project = tmpl_context.project

        f_new.value = dict(proj=project.id, project_name_=project.name)
        tmpl_context.form = f_new
        return dict(title=_('Create a new scene'))

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

        msg = '%s %s' % (_('Created scene:'), scene.path)

        # log into Journal
        journal.add(user, '%s - %s' % (msg, scene))
        
        # notify clients
        updates = [
            dict(item=scene, type='added', topic=TOPIC_SCENES),
            dict(item=project, type='updated', topic=TOPIC_PROJECT_STRUCTURE),
            ]
        notify.send(updates)
        return dict(msg=msg, status='ok', updates=updates)
    
    @project_set_active
    @require(is_project_admin())
    @expose('spam.templates.forms.form')
    def edit(self, proj, sc, **kwargs):
        """Display a EDIT form."""
        scene = scene_get(proj, sc)

        f_edit.value = dict(proj=scene.project.id,
                            sc=scene.name,
                            project_name_=scene.project.name,
                            scene_name_=scene.name,
                            description=scene.description,
                           )
        tmpl_context.form = f_edit
        return dict(title='%s %s' % (_('Edit scene:'), scene.path))
        
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
        if description is not None and not scene.description == description:
            scene.description = description
            modified = True
        
        if modified:
            new = scene.__dict__.copy()

            msg = '%s %s' % (_('Updated scene:'), scene.path)

            # log into Journal
            journal.add(user, '%s - %s' % (msg, diff_dicts(old, new)))
            
            # notify clients
            updates = [dict(item=scene, type='updated', topic=TOPIC_SCENES)]
            notify.send(updates)
            return dict(msg=msg, status='ok', updates=updates)
        return dict(msg='%s %s' % (_('Scene is unchanged:'), scene.path),
                                                    status='info', updates=[])

    @project_set_active
    @require(is_project_admin())
    @expose('spam.templates.forms.form')
    def get_delete(self, proj, sc, **kwargs):
        """Display a DELETE confirmation form."""
        scene = scene_get(proj, sc)

        f_confirm.custom_method = 'DELETE'
        f_confirm.value = dict(proj=scene.project.id,
                               sc=scene.name,
                               project_name_=scene.project.name,
                               scene_name_=scene.name,
                               description_=scene.description,
                              )
        warning = _('This will only delete the scene entry in the database. '
                    'The data must be deleted manually if needed.')
        tmpl_context.form = f_confirm
        return dict(title='%s %s?' % (_('Are you sure you want to delete:'),
                                                scene.path), warning=warning)

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
            return dict(msg='%s %s' % (
                    _('Cannot delete scene because it contains shots:'),
                    scene.path),
                status='error', updates=[])

        session.delete(scene)

        # delete association objects or they will be orphaned
        session.flush()
        session.delete(scene.taggable)
        session.delete(scene.annotable)

        # invalidate project cache
        project.touch()

        msg = '%s %s' % (_('Deleted scene:'), scene.path)

        # log into Journal
        journal.add(user, '%s - %s' % (msg, scene))
        
        # notify clients
        updates = [
            dict(item=scene, type='deleted', topic=TOPIC_SCENES),
            dict(item=project, type='updated', topic=TOPIC_PROJECT_STRUCTURE),
            ]
        notify.send(updates)

        return dict(msg=msg, status='ok', updates=updates)
    
    # Custom REST-like actions
    _custom_actions = []

