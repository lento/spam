# -*- coding: utf-8 -*-
"""User tabs"""

from tg import expose, request, tmpl_context, require
from pylons.i18n import ugettext as _, lazy_ugettext as l_
from repoze.what.predicates import in_group

from spam.lib.base import SPAMBaseController
from spam.model import session_get, User, user_get, Group
from spam.lib.widgets import TableUsers, TableGroupUsers

# livetable widgets
t_users = TableUsers()
t_group_users = TableGroupUsers()

class TabController(SPAMBaseController):
    """The controller for user tabs."""
    @require(in_group('administrators'))
    @expose('spam.templates.user.tabs.users')
    def users(self):
        """Handle the 'users' tab."""
        tmpl_context.t_users = t_users
        users = session_get().query(User)
        return dict(users=users)

    @require(in_group('administrators'))
    @expose('spam.templates.user.tabs.groups')
    def groups(self):
        """Handle the 'groups' tab."""
        tmpl_context.t_group_users = t_group_users
        groups = session_get().query(Group)
        return dict(groups=groups)

