# -*- coding: utf-8 -*-
#
# SPAM Spark Project & Asset Manager
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 3 of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this program; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place - Suite 330,
# Boston, MA 02111-1307, USA.
#
# Original Copyright (c) 2010, Lorenzo Pierfederici <lpierfederici@gmail.com>
# Contributor(s): 
#
"""Shot main controller"""

from tg import expose, url, tmpl_context, validate, require
from tg.controllers import RestController
from tg.decorators import with_trailing_slash
from spam.model import session_get, Project, User, Shot, Tag
from spam.model import scene_get, shot_get, tag_get
from spam.lib.widgets import FormShotNew, FormShotEdit, FormShotConfirm
from spam.lib.widgets import FormShotAddTag, TableShots
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
f_add_tag = FormShotAddTag(action=url('/shot/'))

# livetable widgets
t_shots = TableShots()

class Controller(RestController):
    """REST controller for managing shots."""
    
    tab = TabController()
    
    @project_set_active
    @require(is_project_user())
    @expose('spam.templates.scene.tabs.shots')
    def get_all(self, proj, sc):
        """Return a `tab` page with a list of shots for a scene and a button to
        add new shots.
        
        This page is used as the `shots` tab in the scene view:
        :meth:`spam.controllers.scene.main.get_one`.
        """
        scene = scene_get(proj, sc)
        tmpl_context.scene = scene
        tmpl_context.t_shots = t_shots
        return dict(page='shot', sidebar=('projects', scene.project.id),
                                                            shots=scene.shots)

    @expose('spam.templates.scene.tabs.shots')
    def default(self, proj, sc, *args, **kwargs):
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
    @expose('spam.templates.forms.form')
    def new(self, proj, sc, **kwargs):
        """Display a NEW form."""
        tmpl_context.form = f_new
        scene = scene_get(proj, sc)
        
        fargs = dict(proj=scene.project.id, project_=scene.project.name,
                     sc=scene.name, scene_=scene.name)
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
        project = tmpl_context.project
        session = session_get()
        scene = scene_get(proj, sc)
        
        # add shot to db
        shot = Shot(scene.project.id, sh, parent=scene, description=description,
                    action=action, frames=frames, handle_in=handle_in,
                    handle_out=handle_out)
        session.add(shot)
        session.flush()
        
        # create directories
        repo.shot_create_dirs(scene.project.id, shot)
        
        # invalidate project cache
        project.touch()
        
        # send a stomp message to notify clients
        notify.send(shot, update_type='added')
        notify.send(project)
        return dict(msg='created shot "%s"' % shot.path, result='success')
    
    @project_set_active
    @require(is_project_admin())
    @expose('spam.templates.forms.form')
    def edit(self, proj, sc, sh, **kwargs):
        """Display a EDIT form."""
        tmpl_context.form = f_edit
        shot = shot_get(proj, sc, sh)
        
        fargs = dict(proj=shot.project.id, project_=shot.project.name,
                     sc=shot.parent.name, scene_=shot.parent.name,
                     sh=shot.name, name_=shot.name,
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
                     proj=shot.project.id, project_=shot.project.name,
                     sc=shot.parent.name, scene_=shot.parent.name,
                     sh=shot.name, name_=shot.name,
                     description_=shot.description, action_=shot.action,
                     frames_=shot.frames, handle_in_=shot.handle_in,
                     handle_out_=shot.handle_out)
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
        project = tmpl_context.project
        session = session_get()
        shot = shot_get(proj, sc, sh)
        if shot.assets:
            return dict(msg='cannot delete shot "%s" because it contains '
                            'assets' % shot.path,
                        result='failed')
        
        session.delete(shot)

        # invalidate project cache
        project.touch()
        
        notify.send(shot, update_type='deleted')
        notify.send(project)
        return dict(msg='deleted shot "%s"' % shot.path, result='success')
    
    # Custom REST-like actions
    custom_actions = ['tags', 'add_tag', 'remove_tag',
                      'notes', 'add_note', 'remove_note']

    @project_set_active
    @require(is_project_user())
    @expose('spam.templates.tags')
    def tags(self, proj, sc, sh, **kwargs):
        """Return a html fragment with a list of tags for this shot."""
        shot = shot_get(proj, sc, sh)
        return dict(tags=shot.tags)

    @project_set_active
    @require(is_project_admin())
    @expose('spam.templates.forms.form')
    def get_add_tag(self, proj, sc, sh, **kwargs):
        """Display a ADD_TAG form."""
        tmpl_context.form = f_add_tag
        session = session_get()
        shot = shot_get(proj, sc, sh)
        
        fargs = dict(proj=shot.project.id, sc=shot.parent.name, sh=shot.name,
                     current_tags_=', '.join([t.name for t in shot.tags]),
                    )
        
        tags = session.query(Tag).filter_by(proj_id=proj)
        choices = [(t.id, t.name) for t in tags if t not in shot.tags]
        fcargs = dict(tag_ids=dict(options=choices))
        return dict(title='Add a tag to "%s"' % shot.path,
                                                args=fargs, child_args=fcargs)

    @project_set_active
    @require(is_project_admin())
    @expose('json')
    @expose('spam.templates.forms.result')
    @validate(f_add_tag, error_handler=get_add_tag)
    def post_add_tag(self, proj, sc, sh, tag_ids=[], new_tags=None, **kwargs):
        """Add a tag to a shot."""
        project = tmpl_context.project
        session = session_get()
        shot = shot_get(proj, sc, sh)
        
        tags = [tag_get(proj, int(i)) for i in tag_ids]
        if new_tags:
            tags.extend([tag_get(proj, name) for name in new_tags.split(', ')])
        
        added_tags = []
        for tag in tags:
            if tag not in shot.tags:
                shot.tags.append(tag)
                added_tags.append(tag.name)
        added_tags = ', '.join(added_tags)
        
        #notify.send(tag, update_type='added', shot=shot)
        return dict(msg='added tag(s) "%s" to shot "%s"' % 
                                   (added_tags, shot.path), result='success')
    

