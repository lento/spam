# -*- coding: utf-8 -*-
"""Project tabs controllers"""

from tg import expose, request, tmpl_context, require
from pylons.i18n import ugettext as _, lazy_ugettext as l_
from repoze.what import predicates

from spam.lib.base import SPAMBaseController
from spam.model import project_get_eager, session_get, Category
from spam.lib.predicates import is_project_user, is_project_admin
from spam.lib.widgets import TableProjectAdmins

# live tables
t_project_admins = TableProjectAdmins()

class TabController(SPAMBaseController):
    """The controller for project tabs."""
    def _before(self, *args, **kw):
        proj = request.url.split('/')[-3]
        tmpl_context.project = project_get_eager(proj)

    @require(is_project_user())
    @expose('spam.templates.project.tabs.summary')
    def summary(self):
        """Handle the 'summary' tab."""
        #project = tmpl_context.project
        return dict()

    @require(is_project_user())
    @expose('spam.templates.project.tabs.tasks')
    def tasks(self):
        """Handle the 'tasks' tab."""
        #project = tmpl_context.project
        return dict()

    @require(is_project_admin())
    @expose('spam.templates.project.tabs.users')
    def users(self):
        """Handle the 'users' tab."""
        project = tmpl_context.project
        tmpl_context.t_project_admins = t_project_admins
        categories = session_get().query(Category)
        return dict(categories=categories)
    

