# -*- coding: utf-8 -*-
#
# SPAM Spark Project & Asset Manager
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
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
# Copyright (c) 2009, Lorenzo Pierfederici <lpierfederici@gmail.com>
# Contributor(s): 
#
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
        """Handle the 'users' tab.
        
        This tab allows to add, remove and edit SPAM users. Users added here
        can then be assigned to a project as artists or supervisors in the
        project's ``users`` tab: :meth:`spam.controllers.project.tabs.users`.
        """
        tmpl_context.t_users = t_users
        users = session_get().query(User)
        return dict(users=users)

    @require(in_group('administrators'))
    @expose('spam.templates.user.tabs.groups')
    def groups(self):
        """Handle the 'groups' tab.
        
        This tab allows to add users to the `SPAM administrators` group.
        """
        tmpl_context.t_group_users = t_group_users
        groups = session_get().query(Group)
        return dict(groups=groups)

