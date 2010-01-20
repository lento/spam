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
"""Project tabs"""

from tg import expose, request, tmpl_context, require
from pylons.i18n import ugettext as _, lazy_ugettext as l_
from repoze.what import predicates

from spam.lib.base import SPAMBaseController
from spam.model import session_get, Category, project_get
from spam.lib.predicates import is_project_user, is_project_admin
from spam.lib.widgets import TableProjectAdmins, TableProjectSupervisors
from spam.lib.widgets import TableProjectArtists, BoxStatus

# live widgets
b_status = BoxStatus()
t_project_admins = TableProjectAdmins()
t_project_supervisors = TableProjectSupervisors()
t_project_artists = TableProjectArtists()

class TabController(SPAMBaseController):
    """The controller for project tabs."""
    
    def _before(self, *args, **kw):
        proj = request.url.split('/')[-3]
        tmpl_context.project = project_get(proj)

    @require(is_project_user())
    @expose('spam.templates.project.tabs.summary')
    def summary(self):
        """Handle the 'summary' tab.
        
        This tab offers a quick view on the current status of the project.
        """
        tmpl_context.b_status = b_status
        #project = tmpl_context.project
        return dict()

    @require(is_project_admin())
    @expose('spam.templates.project.tabs.users')
    def users(self):
        """Handle the 'users' tab.
        
        This tab allows to assign users to a category as artists or supervisors,
        and to define project administrators.
        """
        session = session_get()
        project = tmpl_context.project
        tmpl_context.t_project_admins = t_project_admins
        tmpl_context.t_project_supervisors = t_project_supervisors
        tmpl_context.t_project_artists = t_project_artists
        categories = session_get().query(Category)
        supervisors = {}
        for cat in categories:
            supervisors[cat.id] = project.supervisors[cat]
        artists = {}
        for cat in categories:
            artists[cat.id] = project.artists[cat]
        
        return dict(categories=categories, supervisors=supervisors,
                                                                artists=artists)
    

