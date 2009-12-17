# -*- coding: utf-8 -*-
"""Project tabs controllers"""

from tg import expose, request, tmpl_context, require
from pylons.i18n import ugettext as _, lazy_ugettext as l_
from repoze.what import predicates

from spam.lib.base import SPAMBaseController
from spam.model import session_get, Category, project_get
from spam.lib.predicates import is_project_user, is_project_admin
from spam.lib.widgets import TableProjectAdmins, TableProjectSupervisors
from spam.lib.widgets import TableProjectArtists

# live tables
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
        session = session_get()
        project = tmpl_context.project
        tmpl_context.t_project_admins = t_project_admins
        tmpl_context.t_project_supervisors = t_project_supervisors
        tmpl_context.t_project_artists = t_project_artists
        categories = session_get().query(Category)
        supervisors = {}
        for cat in categories:
            supervisors[cat.name] = project.supervisors[cat]
        artists = {}
        for cat in categories:
            artists[cat.name] = project.artists[cat]
        
        return dict(categories=categories, supervisors=supervisors,
                                                                artists=artists)
    

