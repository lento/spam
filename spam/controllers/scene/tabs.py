# -*- coding: utf-8 -*-
"""Project tabs controllers"""

from tg import expose, request, tmpl_context
from pylons.i18n import ugettext as _, lazy_ugettext as l_
from repoze.what import predicates

from spam.lib.base import SPAMBaseController
from spam.model import project_get_eager, scene_get


class TabController(SPAMBaseController):
    """The controller for scene tabs."""
    def _before(self, *args, **kw):
        proj, sc = request.url.split('/')[-4:-2]
        scene = scene_get(proj, sc)
        tmpl_context.project = scene.project
        tmpl_context.scene = scene

    @expose('spam.templates.scene.tabs.summary')
    def summary(self):
        """Handle the 'summary' tab."""
        #project = tmpl_context.project
        return dict()

    @expose('spam.templates.scene.tabs.tasks')
    def tasks(self):
        """Handle the 'tasks' tab."""
        #project = tmpl_context.project
        return dict()


