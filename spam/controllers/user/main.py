# -*- coding: utf-8 -*-
"""User Controller"""
from tg import expose, url, tmpl_context, redirect, validate, require
from tg.controllers import RestController
from tg.decorators import with_trailing_slash
from pylons.i18n import ugettext as _, lazy_ugettext as l_
from spam.model import session_get, User, user_get, group_get
from spam.lib.widgets import FormUserNew, FormUserEdit
from spam.lib.widgets import FormUserConfirm, FormUserAddToGroup
from spam.lib.notifications import notify, TOPIC_GROUPS
from repoze.what.predicates import in_group, not_anonymous

from tabs import TabController

import logging
log = logging.getLogger(__name__)

# form widgets
f_new = FormUserNew(action=url('/user/'))
f_edit = FormUserEdit(action=url('/user/'))
f_confirm = FormUserConfirm(action=url('/user/'))
f_add_to_group = FormUserAddToGroup(action=url('/user/'))

class Controller(RestController):
    
    tab = TabController()
    
    @require(in_group('administrators'))
    @with_trailing_slash
    @expose('spam.templates.tabbed_content')
    def get_all(self):
        tabs = [('Users', 'tab/users'),
                ('Groups', 'tab/groups'),
               ]
        
        return dict(page='admin/users', sidebar=('admin', 'users'), tabs=tabs)

    @require(not_anonymous())
    @expose('json')
    @expose('spam.templates.user.get_one')
    def get_one(self, name):
        """Handle the 'home' page."""
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
    custom_actions = ['add', 'remove']

    @require(in_group('administrators'))
    @expose('spam.templates.forms.form')
    def get_add(self, group_name, **kwargs):
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
    @validate(f_add_to_group, error_handler=get_delete)
    def post_add(self, group_id, userids, **kwargs):
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
    def remove(self, user_name, group_name, **kwargs):
        """Remove a user from a group"""
        user = user_get(user_name)
        group = group_get(group_name)
        group.users.remove(user)
        notify.send(user, update_type='deleted', destination=TOPIC_GROUPS,
                                                    group_name=group.group_name)
        return dict(msg='user "%s" removed from group "%s"' %
                        (user.user_name, group.group_name), result='success')
        

