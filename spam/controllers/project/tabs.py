# -*- coding: utf-8 -*-
"""Project tabs controllers"""

from tg import expose, request, tmpl_context
from pylons.i18n import ugettext as _, lazy_ugettext as l_
from repoze.what import predicates

from spam.lib.base import SPAMBaseController
from spam.model import get_project_eager


class ProjectTabController(SPAMBaseController):
    """The controller for project tabs."""
    def __before__(self, *args, **kw):
        proj = request.url.split('/')[-3]
        tmpl_context.project = get_project_eager(proj)

    @expose('spam.templates.project.tabs.summary')
    def summary(self):
        """Handle the 'summary' tab."""
        #project = tmpl_context.project
        return dict()

    @expose('spam.templates.project.tabs.scenes')
    def scenes(self):
        """Handle the 'scenes' tab."""
        #project = tmpl_context.project
        return dict()

    @expose('spam.templates.project.tabs.tasks')
    def tasks(self):
        """Handle the 'tasks' tab."""
        #project = tmpl_context.project
        return dict()


