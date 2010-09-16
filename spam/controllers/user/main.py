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
"""User main Controller"""

from tg import expose, url, tmpl_context, redirect, validate, require, flash
from tg.controllers import RestController
from tg.decorators import with_trailing_slash
from pylons.i18n import ugettext as _, ungettext as n_, lazy_ugettext as l_
from spam.model import session_get, User, user_get, group_get, project_get
from spam.model import category_get, Supervisor, Artist, diff_dicts
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from spam.lib.exceptions import SPAMDBError, SPAMDBNotFound
from spam.lib.widgets import FormUserNew, FormUserEdit, FormUserChangePassword
from spam.lib.widgets import FormUserConfirm, FormUserAddToGroup
from spam.lib.widgets import FormUserAddAdmins, FormUserAddToCategory
from spam.lib.notifications import notify, TOPIC_USERS, TOPIC_GROUPS
from spam.lib.notifications import TOPIC_PROJECT_ADMINS, TOPIC_PROJECT_ARTISTS
from spam.lib.notifications import TOPIC_PROJECT_SUPERVISORS
from spam.lib.journaling import journal
from spam.lib.decorators import project_set_active
from spam.lib.predicates import is_project_user, is_project_admin
from repoze.what.predicates import in_group, not_anonymous

from tabs import TabController

import logging
log = logging.getLogger(__name__)

# form widgets
f_new = FormUserNew(action=url('/user'))
f_change_password = FormUserChangePassword(action=url('/user'))
f_edit = FormUserEdit(action=url('/user'))
f_confirm = FormUserConfirm(action=url('/user'))
f_add_to_group = FormUserAddToGroup(action=url('/user'))
f_add_admins = FormUserAddAdmins(action=url('/user'))
f_add_to_category = FormUserAddToCategory(action=url('/user'))

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
        return dict(title=_('Create a new user'))

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

        msg = '%s %s' % (_('Created User:'), newuser.id)

        # log into Journal
        journal.add(user, '%s - %s' % (msg, newuser))

        # notify clients
        updates = [dict(item=newuser, type='added', topic=TOPIC_USERS)]
        notify.send(updates)

        return dict(msg=msg, status='ok', updates=updates)

    @require(in_group('administrators'))
    @expose('spam.templates.forms.form')
    def edit(self, user_id, **kwargs):
        """Display a EDIT form."""
        user = user_get(user_id)
        f_edit.value = dict(user_id=user.user_id,
                            user_name_=user.user_name,
                            display_name=user.display_name)
        tmpl_context.form = f_edit
        return dict(title='%s %s' % (_('Edit user:'), user.user_id))
        
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
        if display_name and not edituser.display_name == display_name:
            edituser.display_name = display_name
            modified = True
        
        if modified:
            new = edituser.__dict__.copy()

            msg = '%s %s' % (_('Updated user:'), edituser.user_id)

            # log into Journal
            journal.add(user, '%s - %s' % (msg, diff_dicts(old, new)))

            # notify clients
            updates = [
                dict(item=edituser, type='updated', topic=TOPIC_USERS)
                ]
            notify.send(updates)

            return dict(msg=msg, status='ok', updates=updates)

        return dict(msg='%s %s' % (_('User is unchanged:'), edituser.user_id),
                                                    status='info', updates=[])

    @require(in_group('administrators'))
    @expose('spam.templates.forms.form')
    def get_delete(self, user_id, **kwargs):
        """Display a DELETE confirmation form."""
        user = user_get(user_id)
        f_confirm.custom_method = 'DELETE'
        f_confirm.value = dict(user_id=user.user_id,
                               user_name_=user.user_name,
                               display_name_=user.display_name)
        tmpl_context.form = f_confirm
        return dict(title='%s %s?' % (_('Are you sure you want to delete:'),
                                                                user.user_id))

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

        msg = '%s %s' % (_('Deleted user:'), deluser.user_id)

        # log into Journal
        journal.add(user, '%s - %s' % (msg, deluser))

        # notify clients
        updates = [dict(item=deluser, type='deleted', topic=TOPIC_USERS)]
        notify.send(updates)

        return dict(msg=msg, status='ok', updates=updates)

    # Custom REST-like actions
    _custom_actions = ['add_to_group', 'remove_from_group',
                      'add_admins', 'remove_admin',
                      'add_supervisors', 'remove_supervisor',
                      'add_artists', 'remove_artist',
                      'change_password',
                     ]
                     
    @require(not_anonymous())
    @expose('spam.templates.forms.form')
    def get_change_password(self, **kwargs):
        """Display a NEW form."""
        tmpl_context.form = f_change_password
        return dict(title=_('Change Password for - %s' % tmpl_context.user.user_name))

    @expose('json')
    @expose('spam.templates.forms.result')
    @validate(f_change_password, error_handler=get_change_password)
    def post_change_password(self, new_password, retype_password):
        """Change the current user password"""
        user = tmpl_context.user
        user.password = new_password
        msg = '%s %s' % (_('Changed password for User:'), user.user_id)

        # log into Journal
        journal.add(user, '%s' % msg)

        # notify clients
        updates = [dict(item=user, type='updated', topic=TOPIC_USERS)]
        notify.send(updates)
        return dict(msg=msg, status='ok', updates=updates)

    @require(in_group('administrators'))
    @expose('spam.templates.forms.form')
    def get_add_to_group(self, group_id, **kwargs):
        """Display a ADD users form."""
        group = group_get(group_id)
        users = session_get().query(User)
        choices = [(u.user_id, '%-16s (%s)' % (u.user_id, u.display_name))
                                                                for u in users]
        f_add_to_group.child.children.userids.options = choices
        f_add_to_group.value = dict(group_id=group.group_id)
        tmpl_context.form = f_add_to_group
        return dict(title='%s %s' % (_('Add users to group:'), group.group_id))

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
        updates = []
        
        for uid in userids:
            adduser = user_get(uid)
            if adduser not in group.users:
                group.users.append(adduser)
                added.append(adduser.user_id)
                
                # prepare updates to notify clients
                updates.append(dict(item=adduser, type='added',
                            topic=TOPIC_GROUPS, filter=group.group_name))
        
        added = ', '.join(added)

        if added:
            # log into Journal
            msg = '%s %s %s' % (added,
                                n_('added to group:',
                                   'added to group:', len(added)),
                                group.group_id)
            journal.add(user, msg)
            notify.send(updates)

            return dict(msg=msg, status='ok', updates=updates)

        return dict(msg='%s %s' % (_('Selected users are already in group:'),
                                    group.group_id), status='info', updates=[])

    @expose('json')
#    @expose('spam.templates.forms.result')
    def remove_from_group(self, user_id, group_id):
        """Remove a user from a group"""
        session = session_get()
        user = tmpl_context.user
        remuser = user_get(user_id)
        group = group_get(group_id)
        updates = []
        
        if remuser in group.users:
            group.users.remove(remuser)
            
            # prepare updates to notify clients
            updates.append(dict(item=remuser, type='deleted',
                        topic=TOPIC_GROUPS, filter=group.group_name))

            # log into Journal
            msg = '%s %s %s' % (remuser.user_id,
                                _('removed from group'),
                                group.group_id)
            journal.add(user, msg)
            notify.send(updates)

            return dict(msg=msg, status='ok', updates=updates)

        return dict(msg='%s %s %s' % (remuser.user_id, _('is not in group:'),
                                    group.group_id), status='error', updates=[])
        
    @project_set_active
    @require(is_project_admin())
    @expose('spam.templates.forms.form')
    def get_add_admins(self, proj, **kwargs):
        """Display a ADD users form."""
        project = tmpl_context.project
        users = session_get().query(User)
        choices = [(u.user_id, '%-16s (%s)' % (u.user_id, u.display_name))
                                                                for u in users]
        f_add_admins.value = dict(proj=project.id)
        f_add_admins.child.children.userids.options = choices
        tmpl_context.form = f_add_admins
        return dict(title='%s %s' % (_('Add administrators for:'), project.id))

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
        updates = []

        for uid in userids:
            adduser = user_get(uid)
            if adduser not in project.admins:
                project.admins.append(adduser)
                added.append(adduser.user_id)
                
                # prepare updates to notify clients
                updates.append(dict(item=adduser, type='added',
                            topic=TOPIC_PROJECT_ADMINS, filter=project.id))
            
        added = ', '.join(added)
        
        if added:
            # log into Journal
            msg = '%s %s %s' % (added,
                                n_('set as administrator for:',
                                   'set as administrators for:', len(added)),
                                project.id)
            journal.add(user, msg)
            notify.send(updates)

            return dict(msg=msg, status='ok', updates=updates)

        return dict(msg='%s %s' % (
            _('Selected users are already administrators for:'), project.id),
            status='info', updates=[])

    @project_set_active
    @require(is_project_admin())
    @expose('json')
#    @expose('spam.templates.forms.result')
    def remove_admin(self, proj, user_id):
        """Remove an administrator from a project"""
        session = session_get()
        user = tmpl_context.user
        project = tmpl_context.project
        remuser = user_get(user_id)
        updates = []
        
        if remuser in project.admins:
            project.admins.remove(remuser)
            
            # prepare updates to notify clients
            updates.append(dict(item=remuser, type='deleted',
                        topic=TOPIC_PROJECT_ADMINS, filter=project.id))

            # log into Journal
            msg = '%s %s %s' % (remuser.user_id,
                                _('revoked as administrator for:'),
                                project.id)
            journal.add(user, msg)
            notify.send(updates)

            return dict(msg=msg, status='ok', updates=updates)

        return dict(msg='%s %s %s' % (
                remuser.user_id, _('is not an administrator for:'), project.id),
                status='error', updates=[])

    @project_set_active
    @require(is_project_admin())
    @expose('spam.templates.forms.form')
    def get_add_supervisors(self, proj, category_id, **kwargs):
        """Display a ADD supervisors form."""
        project = tmpl_context.project
        category = category_get(category_id)
        users = session_get().query(User)
        choices = [(u.user_id, '%-16s (%s)' % (u.user_id, u.display_name))
                                                                for u in users]
        f_add_to_category.custom_method = 'ADD_SUPERVISORS'
        f_add_to_category.value = dict(proj=project.id,
                                       category_id=category.id)
        f_add_to_category.child.children.userids.options = choices
        tmpl_context.form = f_add_to_category
        return dict(title='%s %s/%s' % (_('Add supervisors for:'), project.id,
                                                                category.id))

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
        updates = []

        users = [user_get(uid) for uid in userids]
        supervisors = [Supervisor(project.id, category, adduser) for adduser in
                        users if adduser not in project.supervisors[category]]
        for supervisor in supervisors:
            added.append(supervisor.user.user_id)

            # prepare updates to notify clients
            updates.append(dict(item=supervisor.user, type='added',
                        topic=TOPIC_PROJECT_SUPERVISORS,
                        filter='%s-%s' % (project.id, category.id)))

        added = ', '.join(added)

        if added:
            # log into Journal
            msg = '%s %s %s/%s' % (added,
                                   n_('set as supervisor for:',
                                      'set as supervisors for:', len(added)),
                                   project.id, category.id)
            journal.add(user, msg)
            notify.send(updates)

            return dict(msg=msg, status='ok', updates=updates)

        return dict(msg='%s %s' % (
                _('Selected users are already supervisors for:'), project.id),
                status='info', updates=[])

    @project_set_active
    @require(is_project_admin())
    @expose('json')
#    @expose('spam.templates.forms.result')
    def remove_supervisor(self, proj, category_id, user_id):
        """Remove a supervisor from a category"""
        session = session_get()
        user = tmpl_context.user
        project = tmpl_context.project
        category = category_get(category_id)
        remuser = user_get(user_id)
        updates = []

        if remuser in project.supervisors[category]:
            query = session.query(Supervisor).filter_by(proj_id=project.id)
            query = query.filter_by(category_id=category.id)
            query = query.filter_by(user_id=remuser.user_id)
            sup = query.one()
            session.delete(sup)

            # prepare updates to notify clients
            updates.append(dict(item=remuser, type='deleted',
                        topic=TOPIC_PROJECT_SUPERVISORS,
                        filter='%s-%s' % (project.id, category.id)))

            # log into Journal
            msg = '%s %s %s/%s' % (remuser.user_id,
                                   _('revoked as supervisor from:'),
                                   project.id, category.id)
            journal.add(user, msg)
            notify.send(updates)

            return dict(msg=msg, status='ok', updates=updates)

        return dict(msg='%s %s %s' % (
                remuser.user_id, _('is not a supervisor for:'), project.id),
                status='error', updates=[])

    @project_set_active
    @require(is_project_admin())
    @expose('spam.templates.forms.form')
    def get_add_artists(self, proj, category_id, **kwargs):
        """Display a ADD artists form."""
        project = tmpl_context.project
        category = category_get(category_id)
        users = session_get().query(User)
        choices = [(u.user_id, '%-16s (%s)' % (u.user_id, u.display_name))
                                                                for u in users]
        f_add_to_category.custom_method = 'ADD_ARTISTS'
        f_add_to_category.value = dict(proj=project.id,
                                       category_id=category.id)
        f_add_to_category.child.children.userids.options = choices
        tmpl_context.form = f_add_to_category
        return dict(title='%s %s/%s' % (_('Add artists for:'), project.id,
                                                                category.id))

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
        updates = []

        users = [user_get(uid) for uid in userids]
        artists = [Artist(project.id, category, adduser) for adduser in users if
                                    adduser not in project.artists[category]]
        for artist in artists:
            added.append(artist.user.user_id)

            # prepare updates to notify clients
            updates.append(dict(item=artist.user, type='added',
                        topic=TOPIC_PROJECT_ARTISTS,
                        filter='%s-%s' % (project.id, category.id)))

        added = ', '.join(added)

        if added:
            # log into Journal
            msg = '%s %s %s/%s' % (added,
                                   n_('set as artist for:',
                                      'set as artists for:', len(added)),
                                   project.id, category.id)
            journal.add(user, msg)
            notify.send(updates)

            return dict(msg=msg, status='ok', updates=updates)

        return dict(msg='%s %s' % (
                _('Selected users are already artists for:'), project.id),
                status='info', updates=[])

    @project_set_active
    @require(is_project_admin())
    @expose('json')
#    @expose('spam.templates.forms.result')
    def remove_artist(self, proj, category_id, user_id):
        """Remove an artist from a category"""
        session = session_get()
        user = tmpl_context.user
        project = project_get(proj)
        category = category_get(category_id)
        remuser = user_get(user_id)
        updates = []

        if remuser in project.artists[category]:
            query = session.query(Artist).filter_by(proj_id=project.id)
            query = query.filter_by(category_id=category.id)
            query = query.filter_by(user_id=remuser.user_id)
            artist = query.one()
            session.delete(artist)

            # prepare updates to notify clients
            updates.append(dict(item=remuser, type='deleted',
                        topic=TOPIC_PROJECT_ARTISTS,
                        filter='%s-%s' % (project.id, category.id)))

            # log into Journal
            msg = '%s %s %s/%s' % (remuser.user_id,
                                   _('revoked as artist from:'),
                                   project.id, category.id)
            journal.add(user, msg)
            notify.send(updates)

            return dict(msg=msg, status='ok', updates=updates)

        return dict(msg='%s %s %s' % (
                remuser.user_id, _('is not an artist for:'), project.id),
                status='error', updates=[])

