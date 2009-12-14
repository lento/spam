# -*- coding: utf-8 -*-
"""User Controller"""
from tg import expose, url, tmpl_context, redirect, validate, require
from tg.controllers import RestController
from pylons.i18n import ugettext as _, lazy_ugettext as l_
from spam.model import session_get, User, user_get
from spam.lib.widgets import FormUserNew, FormUserEdit
from spam.lib.widgets import FormUserConfirm, TableUsers
from spam.lib.notifications import notify
from repoze.what.predicates import in_group, not_anonymous

import logging
log = logging.getLogger(__name__)

# form widgets
f_new = FormUserNew(action=url('/user/'))
f_edit = FormUserEdit(action=url('/user/'))
f_confirm = FormUserConfirm(action=url('/user/'))

# livetable widgets
t_users = TableUsers()

class Controller(RestController):
    
    @require(in_group('administrators'))
    @expose('spam.templates.user.get_all')
    def get_all(self):
        tmpl_context.t_users = t_users
        users = session_get().query(User)
        return dict(page='admin/users', sidebar=('admin', 'users'), users=users)

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
    custom_actions = []

