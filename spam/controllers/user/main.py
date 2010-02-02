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
from spam.model import category_get, Supervisor, Artist, diff_dicts
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from spam.lib.exceptions import SPAMDBError, SPAMDBNotFound
from spam.lib.widgets import FormUserNew, FormUserEdit
from spam.lib.widgets import FormUserConfirm, FormUserAddToGroup
from spam.lib.widgets import FormUserAddAdmins, FormUserAddToCategory
from spam.lib.notifications import notify
from spam.lib.journaling import journal
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
    def post(self, user_name, display_name, password):
        """Create a new user"""
        session = session_get()
        user = tmpl_context.user
        
        # add user to shared db
        newuser = User(user_name, display_name=display_name)
        newuser.password = password
        session.add(newuser)
        session.flush()
        
        # log into Journal
        journal.add(user, 'created %s' % newuser)
        
        # send a stomp message to notify clients
        notify.send(newuser, update_type='added')
        return dict(msg='created user "%s"' % newuser.id, result='success',
                                                                user=newuser)
    
    @require(in_group('administrators'))
    @expose('spam.templates.forms.form')
    def edit(self, user_id, **kwargs):
        """Display a EDIT form."""
        tmpl_context.form = f_edit
        user = user_get(user_id)
        fargs = dict(user_id=user.user_id, user_name_=user.user_name,
                     display_name=user.display_name)
        fcargs = dict()
        return dict(title='Edit user "%s"' % user.user_id, args=fargs,
                                                            child_args=fcargs)
        
    @require(in_group('administrators'))
    @expose('json')
    @expose('spam.templates.forms.result')
    @validate(f_edit, error_handler=edit)
    def put(self, user_id, display_name=None):
        """Edit a user"""
        session = session_get()
        user = tmpl_context.user
        edituser = user_get(user_id)
        old = edituser.__dict__.copy()
        
        modified = False
        if display_name:
            edituser.display_name = display_name
            modified = True
        
        if modified:
            new = edituser.__dict__.copy()

            # log into Journal
            journal.add(user, 'modified %s: %s' %
                                            (edituser, diff_dicts(old, new)))
            
            # send a stomp message to notify clients
            notify.send(edituser)
            return dict(msg='updated user "%s"' %
                                            edituser.user_id, result='success')
        return dict(msg='user "%s" unchanged' %
                                            edituser.user_id, result='success')

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
                title='Are you sure you want to delete "%s"?' % user.user_id,
                args=fargs, child_args=fcargs)

    @require(in_group('administrators'))
    @expose('json')
    @expose('spam.templates.forms.result')
    @validate(f_confirm, error_handler=get_delete)
    def post_delete(self, user_id):
        """Delete a user."""
        session = session_get()
        user = tmpl_context.user
        deluser = user_get(user_id)

        session.delete(deluser)

        # log into Journal
        journal.add(user, 'deleted %s' % deluser)
        
        # send a stomp message to notify clients
        notify.send(deluser, update_type='deleted')
        return dict(msg='deleted user "%s"' % deluser.user_id, result='success')

    # Custom REST-like actions
    custom_actions = ['add_to_group', 'remove_from_group',
                      'add_admins', 'remove_admin',
                      'add_supervisors', 'remove_supervisor',
                      'add_artists', 'remove_artist',
                     ]

    @require(in_group('administrators'))
    @expose('spam.templates.forms.form')
    def get_add_to_group(self, group_id, **kwargs):
        """Display a ADD users form."""
        tmpl_context.form = f_add_to_group
        group = group_get(group_id)
        users = session_get().query(User)
        choices = [(u.user_id, '%-16s (%s)' % (u.user_id, u.display_name))
                                                                for u in users]
        fargs = dict(group_id=group.group_id,)
        fcargs = dict(userids=dict(options=choices))
        return dict(title='Add users to group "%s"' % group.group_id,
                                                args=fargs, child_args=fcargs)

    @require(in_group('administrators'))
    @expose('json')
    @expose('spam.templates.forms.result')
    @validate(f_add_to_group, error_handler=get_add_to_group)
    def post_add_to_group(self, group_id, userids):
        """Add users to a group"""
        session = session_get()
        user = tmpl_context.user
        group = group_get(group_id)
        added = []
        
        for uid in userids:
            adduser = user_get(uid)
            if adduser not in group.users:
                group.users.append(adduser)
                added.append(adduser.user_id)
                
                # send a stomp message to notify clients
                notify.send(adduser, update_type='added',
                            destination=notify.TOPIC_GROUPS,
                            group_name=group.group_name)
        
        added = ', '.join(added)
        
        # log into Journal
        journal.add(user, 'added user(s) "%s" to %s' % (added, group))
        
        return dict(msg='added user(s) %s to group "%s"' %
                                    (added, group.group_id), result='success')

    @expose('json')
    @expose('spam.templates.forms.result')
    def remove_from_group(self, user_id, group_id):
        """Remove a user from a group"""
        session = session_get()
        user = tmpl_context.user
        remuser = user_get(user_id)
        group = group_get(group_id)
        
        group.users.remove(remuser)
        
        # log into Journal
        journal.add(user, 'removed user "%s" from %s' % (remuser, group))
        
        # send a stomp message to notify clients
        notify.send(remuser, update_type='deleted',
                    destination=notify.TOPIC_GROUPS,
                    group_name=group.group_name)
        return dict(msg='user "%s" removed from group "%s"' %
                        (remuser.user_id, group.group_id), result='success')
        
    @project_set_active
    @require(is_project_admin())
    @expose('spam.templates.forms.form')
    def get_add_admins(self, proj, **kwargs):
        """Display a ADD users form."""
        tmpl_context.form = f_add_admins
        project = tmpl_context.project
        users = session_get().query(User)
        choices = [(u.user_id, '%-16s (%s)' % (u.user_id, u.display_name))
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
    def post_add_admins(self, proj, userids):
        """Add administrators to a project"""
        session = session_get()
        user = tmpl_context.user
        project = tmpl_context.project
        added = []

        for uid in userids:
            adduser = user_get(uid)
            if adduser not in project.admins:
                project.admins.append(adduser)
                added.append(adduser.user_id)
                
                # send a stomp message to notify clients
                notify.send(adduser, update_type='added', proj=project.id,
                            destination=notify.TOPIC_PROJECT_ADMINS)
            
        added = ', '.join(added)
        
        # log into Journal
        journal.add(user, 'added user(s) "%s" to "%s" administrators' %
                                                        (added, project.id))
        
        return dict(msg='added user(s) %s to "%s" administrators' %
                                        (added, project.id), result='success')

    @project_set_active
    @require(is_project_admin())
    @expose('json')
    @expose('spam.templates.forms.result')
    def remove_admin(self, proj, user_id):
        """Remove an administrator from a project"""
        session = session_get()
        user = tmpl_context.user
        project = tmpl_context.project
        remuser = user_get(user_id)
        
        if remuser in project.admins:
            project.admins.remove(remuser)
            
            # log into Journal
            journal.add(user, 'removed %s from "%s" administrators' %
                                                        (remuser, project.id))
            
            # send a stomp message to notify clients
            notify.send(remuser, update_type='deleted', proj=project.id,
                        destination=notify.TOPIC_PROJECT_ADMINS)
            return dict(msg='user "%s" removed from "%s" administrators' %
                        (remuser.user_id, project.id), result='success')
        return dict(msg='user "%s" cannot be removed from "%s" administrators' %
                        (remuser.user_id, project.id), result='failed')

    @project_set_active
    @require(is_project_admin())
    @expose('spam.templates.forms.form')
    def get_add_supervisors(self, proj, category_id, **kwargs):
        """Display a ADD supervisors form."""
        tmpl_context.form = f_add_to_category
        project = tmpl_context.project
        category = category_get(category_id)
        users = session_get().query(User)
        choices = [(u.user_id, '%-16s (%s)' % (u.user_id, u.display_name))
                                                                for u in users]
        fargs = dict(_method='ADD_SUPERVISORS', proj=project.id,
                                                        category_id=category.id)
        fcargs = dict(userids=dict(options=choices))
        return dict(title='Add "%s" supervisors for "%s"' %
                    (category.id, project.id), args=fargs, child_args=fcargs)

    @project_set_active
    @require(is_project_admin())
    @expose('json')
    @expose('spam.templates.forms.result')
    @validate(f_add_to_category, error_handler=get_add_supervisors)
    def post_add_supervisors(self, proj, category_id, userids):
        """Add supervisors to a category"""
        session = session_get()
        user = tmpl_context.user
        project = tmpl_context.project
        category = category_get(category_id)
        added = []
        
        users = [user_get(uid) for uid in userids]
        supervisors = [Supervisor(project.id, category, adduser) for adduser in
                        users if adduser not in project.supervisors[category]]
        for supervisor in supervisors:
            added.append(supervisor.user.user_id)

            # send a stomp message to notify clients
            notify.send(supervisor.user, update_type='added', proj=project.id,
                        cat=category.id,
                        destination=notify.TOPIC_PROJECT_SUPERVISORS)
        
        added = ', '.join(added)
        
        # log into Journal
        journal.add(user, 'added %s "%s" supervisor(s) %s' %
                                            (project.id, category.id, added))
        
        return dict(msg='added %s "%s" supervisor(s) %s' %
                            (project.id, category.id, added), result='success')

    @project_set_active
    @require(is_project_admin())
    @expose('json')
    @expose('spam.templates.forms.result')
    def remove_supervisor(self, proj, category_id, user_id):
        """Remove a supervisor from a category"""
        session = session_get()
        user = tmpl_context.user
        project = tmpl_context.project
        category = category_get(category_id)
        remuser = user_get(user_id)
        
        if remuser in project.supervisors[category]:
            query = session.query(Supervisor).filter_by(proj_id=project.id)
            query = query.filter_by(category_id=category.id)
            query = query.filter_by(user_id=remuser.user_id)
            sup = query.one()
            session.delete(sup)

            # log into Journal
            journal.add(user, 'removed %s "%s" supervisor %s' %
                                            (project.id, category.id, remuser))
            
            # send a stomp message to notify clients
            notify.send(remuser, update_type='deleted', proj=project.id,
                        cat=category.id,
                        destination=notify.TOPIC_PROJECT_SUPERVISORS)
            return dict(msg='removed %s "%s" supervisor "%s"' %
                (project.id, category.id, remuser.user_id), result='success')
        return dict(msg='%s "%s" supervisor "%s" cannot be removed' %
                (project.id, category.id, remuser.user_id), result='failed')

    @project_set_active
    @require(is_project_admin())
    @expose('spam.templates.forms.form')
    def get_add_artists(self, proj, category_id, **kwargs):
        """Display a ADD artists form."""
        tmpl_context.form = f_add_to_category
        project = tmpl_context.project
        category = category_get(category_id)
        users = session_get().query(User)
        choices = [(u.user_id, '%-16s (%s)' % (u.user_id, u.display_name))
                                                                for u in users]
        fargs = dict(_method='ADD_ARTISTS', proj=project.id,
                                                        category_id=category.id)
        fcargs = dict(userids=dict(options=choices))
        return dict(title='Add "%s" artists for "%s"' %
                    (category.id, project.id), args=fargs, child_args=fcargs)

    @project_set_active
    @require(is_project_admin())
    @expose('json')
    @expose('spam.templates.forms.result')
    @validate(f_add_to_category, error_handler=get_add_artists)
    def post_add_artists(self, proj, category_id, userids):
        """Add artists to a category"""
        session = session_get()
        user = tmpl_context.user
        project = tmpl_context.project
        category = category_get(category_id)
        added = []
        
        users = [user_get(uid) for uid in userids]
        artists = [Artist(project.id, category, adduser) for adduser in users if
                                    adduser not in project.artists[category]]
        for artist in artists:
            added.append(artist.user.user_id)

            # send a stomp message to notify clients
            notify.send(artist.user, update_type='added', proj=project.id,
                            cat=category.id,
                            destination=notify.TOPIC_PROJECT_ARTISTS)
        
        added = ', '.join(added)
        
        # log into Journal
        journal.add(user, 'added %s "%s" artist(s) %s' %
                                            (project.id, category.id, added))
        
        return dict(msg='added %s "%s" artist(s) %s' %
                            (project.id, category.id, added), result='success')

    @project_set_active
    @require(is_project_admin())
    @expose('json')
    @expose('spam.templates.forms.result')
    def remove_artist(self, proj, category_id, user_id):
        """Remove an artist from a category"""
        session = session_get()
        user = tmpl_context.user
        project = project_get(proj)
        category = category_get(category_id)
        remuser = user_get(user_id)

        if remuser in project.artists[category]:
            query = session.query(Artist).filter_by(proj_id=project.id)
            query = query.filter_by(category_id=category.id)
            query = query.filter_by(user_id=remuser.user_id)
            artist = query.one()
            session.delete(artist)

            # log into Journal
            journal.add(user, 'removed %s "%s" artist %s' %
                                            (project.id, category.id, remuser))
            
            # send a stomp message to notify clients
            notify.send(remuser, update_type='deleted', proj=project.id,
                        cat=category.id,
                        destination=notify.TOPIC_PROJECT_ARTISTS)
            return dict(msg='removed %s "%s" artist "%s"' %
                (project.id, category.id, remuser.user_id), result='success')
        return dict(msg='%s "%s" artist "%s" cannot be removed' %
                (project.id, category.id, remuser.user_id), result='failed')

