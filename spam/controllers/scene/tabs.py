# -*- coding: utf-8 -*-
"""Project tabs controllers"""

from tg import expose, request, tmpl_context
from pylons.i18n import ugettext as _, lazy_ugettext as l_
from repoze.what import predicates

from spam.lib.base import SPAMBaseController
from spam.model import project_get_eager, scene_get


class TabController(SPAMBaseController):
    """The controller for scene tabs."""
    def __before__(self, *args, **kw):
        proj, sc = request.url.split('/')[-4:-2]
        project = project_get_eager(proj)
        tmpl_context.project = project
        scene = scene_get(project.id, sc)
        tmpl_context.scene = scene

    @expose('spam.templates.scene.tabs.summary')
    def summary(self):
        """Handle the 'summary' tab."""
        #project = tmpl_context.project
        return dict()

    @expose('spam.templates.scene.tabs.shots')
    def shots(self):
        """Handle the 'shots' tab."""
        #project = tmpl_context.project
        return dict()

    @expose('spam.templates.scene.tabs.tasks')
    def tasks(self):
        """Handle the 'tasks' tab."""
        #project = tmpl_context.project
        return dict()


