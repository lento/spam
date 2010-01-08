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
"""User main Controller"""

from tg import expose, url, tmpl_context, redirect, validate, require
from tg.controllers import RestController
from tg.decorators import with_trailing_slash
from pylons.i18n import ugettext as _, lazy_ugettext as l_
from spam.model import session_get, User, user_get, group_get, project_get
from spam.model import category_get, Supervisor, Artist
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from spam.lib.exceptions import SPAMDBError, SPAMDBNotFound
from spam.lib.widgets import FormUserNew, FormUserEdit
from spam.lib.widgets import FormUserConfirm, FormUserAddToGroup
from spam.lib.widgets import FormUserAddAdmins, FormUserAddToCategory
from spam.lib.notifications import notify, TOPIC_GROUPS, TOPIC_PROJECT_ADMINS
from spam.lib.notifications import TOPIC_PROJECT_SUPERVISORS
from spam.lib.notifications import TOPIC_PROJECT_ARTISTS
from spam.lib.decorators import project_set_active
from spam.lib.predicates import is_project_user, is_project_admin
from repoze.what.predicates import in_group, not_anonymous

from tabs import TabController

import logging
log = logging.getLogger(__name__)

# form widgets
f_new = FormUserNew(action=url('/user/'))
f_edit = FormUserEdit(action=url('/user/'))
f_confirm = FormUserConfirm(action=url('/user/'))
f_add_to_group = FormUserAddToGroup(action=url('/user/'))
f_add_admins = FormUserAddAdmins(action=url('/user/'))
f_add_to_category = FormUserAddToCategory(action=url('/user/'))

class Controller(RestController):
    """REST controller for managing users.
    
    In addition to the standard REST verbs this controller defines the following
    REST-like methods: 
        * ``add_to_group``      (:meth:`get_add_to_group`, :meth:`post_add_to_group`)
        * ``remove_from_group`` (:meth:`remove_from_group`)
        * ``add_admins``        (:meth:`get_add_admins`, :meth:`post_add_admins`)
        * ``remove_admin``      (:meth:`remove_admin`)
        * ``add_supervisors``   (:meth:`get_add_supervisors`, :meth:`post_add_supervisors`)
        * ``remove_supervisor`` (:meth:`remove_supervisor`)
        * ``add_artists``       (:meth:`get_add_artists`, :meth:`post_add_artists`)
        * ``remove_artist``     (:meth:`remove_artist`)
    """
    
    tab = TabController()
    
    @require(in_group('administrators'))
    @with_trailing_slash
    @expose('spam.templates.tabbed_content')
    def get_all(self):
        """Return a `tabbed` page for user tabs."""
        tabs = [('Users', 'tab/users'),
                ('Groups', 'tab/groups'),
               ]
        
        return dict(page='admin/users', sidebar=('admin', 'users'), tabs=tabs)

    @require(not_anonymous())
    @expose('json')
    @expose('spam.templates.user.get_one')
    def get_one(self, name):
        """Handle the `home` page."""
        return dict(page="%s's home" % tmpl_context.user.user_name,
                                                    sidebar=('user', 'home'))

    @require(in_group('administrators'))
    @expose('spam.templates.forms.form')
    def new(self, **kwargs):
        """Display a NEW form."""
        tmpl_context.form = f_new
        fargs = dict()
        fcargs = dict()
        return dict(title='Create a new user', args=fargs,
                                                            child_args=fcargs)

    @require(in_group('administrators'))
    @expose('json')
    @expose('spam.templates.forms.result')
    @validate(f_new, error_handler=new)
    def post(self, user_name, display_name, password, **kwargs):
        """Create a new user"""
        session = session_get()
        
        # add user to shared db
        user = User()
        user.user_name = user_name
        user.display_name = display_name
        user.password = password
        session.add(user)
        session.flush()
        
        # send a stomp message to notify clients
        notify.send(user, update_type='added')
        return dict(msg='created user "%s"' % user_name, result='success')
    
    @require(in_group('administrators'))
    @expose('spam.templates.forms.form')
    def edit(self, user_name, **kwargs):
        """Display a EDIT form."""
        tmpl_context.form = f_edit
        user = user_get(user_name)
        fargs = dict(user_id=user.user_id, user_name=user.user_name,
                     display_name=user.display_name)
        fcargs = dict()
        return dict(title='Edit user "%s"' % user.user_name, args=fargs,
                                                            child_args=fcargs)
        
    @require(in_group('administrators'))
    @expose('json')
    @expose('spam.templates.forms.result')
    @validate(f_edit, error_handler=edit)
    def put(self, user_id, user_name, display_name, **kwargs):
        """Edit a user"""
        user = user_get(user_id)
        user.user_name = user_name
        user.display_name = display_name
        notify.send(user)
        return dict(msg='updated user "%s"' % user_name, result='success')

    @require(in_group('administrators'))
    @expose('spam.templates.forms.form')
    def get_delete(self, user_id, **kwargs):
        """Display a DELETE confirmation form."""
        tmpl_context.form = f_confirm
        user = user_get(user_id)
        fargs = dict(_method='DELETE', user_id=user.user_id,
                     user_name_=user.user_name, display_name_=user.display_name)
        fcargs = dict()
        return dict(
                title='Are you sure you want to delete "%s"?' % user.user_name,
                args=fargs, child_args=fcargs)

    @require(in_group('administrators'))
    @expose('json')
    @expose('spam.templates.forms.result')
    @validate(f_confirm, error_handler=get_delete)
    def post_delete(self, user_id, **kwargs):
        """Delete a user."""
        session = session_get()
        user = user_get(user_id)
        session.delete(user)
        notify.send(user, update_type='deleted')
        return dict(msg='deleted user "%s"' % user.user_name, result='success')

    # Custom REST-like actions
    custom_actions = ['add_to_group', 'remove_from_group',
                      'add_admins', 'remove_admin',
                      'add_supervisors', 'remove_supervisor',
                      'add_artists', 'remove_artist',
                     ]

    @require(in_group('administrators'))
    @expose('spam.templates.forms.form')
    def get_add_to_group(self, group_name, **kwargs):
        """Display a ADD users form."""
        tmpl_context.form = f_add_to_group
        group = group_get(group_name)
        users = session_get().query(User)
        choices = [(u.user_id, '%-16s (%s)' % (u.user_name, u.display_name))
                                                                for u in users]
        fargs = dict(group_id=group.group_id,)
        fcargs = dict(userids=dict(options=choices))
        return dict(title='Add users to group "%s"' % group_name,
                                                args=fargs, child_args=fcargs)

    @require(in_group('administrators'))
    @expose('json')
    @expose('spam.templates.forms.result')
    @validate(f_add_to_group, error_handler=get_add_to_group)
    def post_add_to_group(self, group_id, userids, **kwargs):
        """Add users to a group"""
        session = session_get()
        group = group_get(group_id)
        added = []
        for uid in userids:
            user = user_get(int(uid))
            if user not in group.users:
                group.users.append(user)
                added.append(user.user_name)
                notify.send(user, update_type='added', destination=TOPIC_GROUPS,
                                                    group_name=group.group_name)
            
        return dict(msg='added user(s) %s to group "%s"' %
                                    (added, group.group_name), result='success')

    @expose('json')
    @expose('spam.templates.forms.result')
    def remove_from_group(self, user_name, group_name, **kwargs):
        """Remove a user from a group"""
        user = user_get(user_name)
        group = group_get(group_name)
        group.users.remove(user)
        notify.send(user, update_type='deleted', destination=TOPIC_GROUPS,
                                                    group_name=group.group_name)
        return dict(msg='user "%s" removed from group "%s"' %
                        (user.user_name, group.group_name), result='success')
        
    @project_set_active
    @require(is_project_admin())
    @expose('spam.templates.forms.form')
    def get_add_admins(self, proj, **kwargs):
        """Display a ADD users form."""
        tmpl_context.form = f_add_admins
        project = tmpl_context.project
        users = session_get().query(User)
        choices = [(u.user_id, '%-16s (%s)' % (u.user_name, u.display_name))
                                                                for u in users]
        fargs = dict(proj=project.id)
        fcargs = dict(userids=dict(options=choices))
        return dict(title='Add users to "%s" administrators' % project.id,
                                                args=fargs, child_args=fcargs)

    @project_set_active
    @require(is_project_admin())
    @expose('json')
    @expose('spam.templates.forms.result')
    @validate(f_add_admins, error_handler=get_add_admins)
    def post_add_admins(self, proj, userids, **kwargs):
        """Add administrators to a project"""
        session = session_get()
        project = tmpl_context.project
        session.refresh(project)
        added = []
        for uid in userids:
            user = user_get(int(uid))
            if user not in project.admins:
                project.admins.append(user)
                added.append(user.user_name)
                notify.send(user, update_type='added', proj=project.id,
                                            destination=TOPIC_PROJECT_ADMINS)
        session.flush()
            
        return dict(msg='added user(s) %s to "%s" administrators' %
                                        (added, project.id), result='success')

    @project_set_active
    @require(is_project_admin())
    @expose('json')
    @expose('spam.templates.forms.result')
    def remove_admin(self, proj, user_name, **kwargs):
        """Remove an administrator from a project"""
        session = session_get()
        user = user_get(user_name)
        project = tmpl_context.project
        session.refresh(project)
        if user in project.admins:
            project.admins.remove(user)
            session.flush()
            notify.send(user, update_type='deleted', proj=project.id,
                                            destination=TOPIC_PROJECT_ADMINS)
            return dict(msg='user "%s" removed from "%s" administrators' %
                        (user.user_name, project.id), result='success')
        return dict(msg='user "%s" cannot be removed from "%s" administrators' %
                        (user.user_name, project.id), result='failed')

    @project_set_active
    @require(is_project_admin())
    @expose('spam.templates.forms.form')
    def get_add_supervisors(self, proj, category_id, **kwargs):
        """Display a ADD supervisors form."""
        tmpl_context.form = f_add_to_category
        project = tmpl_context.project
        category = category_get(category_id)
        users = session_get().query(User)
        choices = [(u.user_id, '%-16s (%s)' % (u.user_name, u.display_name))
                                                                for u in users]
        fargs = dict(_method='ADD_SUPERVISORS', proj=project.id,
                                                        category_id=category.id)
        fcargs = dict(userids=dict(options=choices))
        return dict(title='Add "%s" supervisors for "%s"' %
                    (category.name, project.id), args=fargs, child_args=fcargs)

    @project_set_active
    @require(is_project_admin())
    @expose('json')
    @expose('spam.templates.forms.result')
    @validate(f_add_to_category, error_handler=get_add_supervisors)
    def post_add_supervisors(self, proj, category_id, userids, **kwargs):
        """Add supervisors to a category"""
        session = session_get()
        project = tmpl_context.project
        category = category_get(category_id)
        users = [user_get(int(uid)) for uid in userids]
        supervisors = [Supervisor(project.id, category, user) for user in users
                                if user not in project.supervisors[category]]
        added = []
        for supervisor in supervisors:
            added.append(supervisor.user.user_name)
            notify.send(supervisor.user, update_type='added', proj=project.id,
                            cat=category.name,
                            destination=TOPIC_PROJECT_SUPERVISORS)
        
        return dict(msg='added "%s" supervisor(s) %s' %
                            (category.name, ', '.join(added)), result='success')

    @project_set_active
    @require(is_project_admin())
    @expose('json')
    @expose('spam.templates.forms.result')
    def remove_supervisor(self, proj, category_id, user_name, **kwargs):
        """Remove a supervisor from a category"""
        session = session_get()
        project = tmpl_context.project
        category = category_get(category_id)
        user = user_get(user_name)
        if user in project.supervisors[category]:
            query = session.query(Supervisor).filter_by(proj_id=project.id)
            query = query.filter_by(category_id=category.id)
            query = query.filter_by(user_id=user.id)
            sup = query.one()
            session.delete(sup)
            notify.send(user, update_type='deleted', proj=project.id,
                        cat=category.name,
                        destination=TOPIC_PROJECT_SUPERVISORS)
            return dict(msg='removed "%s" supervisor "%s"' %
                        (category.name, user.user_name), result='success')
        return dict(msg='"%s" supervisor "%s" cannot be removed' %
                        (category.name, user.user_name), result='failed')

    @project_set_active
    @require(is_project_admin())
    @expose('spam.templates.forms.form')
    def get_add_artists(self, proj, category_id, **kwargs):
        """Display a ADD artists form."""
        tmpl_context.form = f_add_to_category
        project = tmpl_context.project
        category = category_get(category_id)
        users = session_get().query(User)
        choices = [(u.user_id, '%-16s (%s)' % (u.user_name, u.display_name))
                                                                for u in users]
        fargs = dict(_method='ADD_ARTISTS', proj=project.id,
                                                        category_id=category.id)
        fcargs = dict(userids=dict(options=choices))
        return dict(title='Add "%s" artists for "%s"' %
                    (category.name, project.id), args=fargs, child_args=fcargs)

    @project_set_active
    @require(is_project_admin())
    @expose('json')
    @expose('spam.templates.forms.result')
    @validate(f_add_to_category, error_handler=get_add_artists)
    def post_add_artists(self, proj, category_id, userids, **kwargs):
        """Add artists to a category"""
        session = session_get()
        project = tmpl_context.project
        category = category_get(category_id)
        users = [user_get(int(uid)) for uid in userids]
        artists = [Artist(project.id, category, user) for user in users if
                                        user not in project.artists[category]]
        added = []
        for artist in artists:
            added.append(artist.user.user_name)
            notify.send(artist.user, update_type='added', proj=project.id,
                            cat=category.name,
                            destination=TOPIC_PROJECT_ARTISTS)
        
        return dict(msg='added "%s" artist(s) %s' %
                            (category.name, ', '.join(added)), result='success')

    @project_set_active
    @require(is_project_admin())
    @expose('json')
    @expose('spam.templates.forms.result')
    def remove_artist(self, proj, category_id, user_name, **kwargs):
        """Remove an artist from a category"""
        session = session_get()
        project = project_get(proj)
        #session.refresh(project)
        category = category_get(category_id)
        user = user_get(user_name)
        if user in project.artists[category]:
            query = session.query(Artist).filter_by(proj_id=project.id)
            query = query.filter_by(category_id=category.id)
            query = query.filter_by(user_id=user.id)
            artist = query.one()
            session.delete(artist)
            notify.send(user, update_type='deleted', proj=project.id,
                        cat=category.name,
                        destination=TOPIC_PROJECT_ARTISTS)
            return dict(msg='removed "%s" artist "%s"' %
                        (category.name, user.user_name), result='success')
        return dict(msg='"%s" artist "%s" cannot be removed' %
                        (category.name, user.user_name), result='failed')

