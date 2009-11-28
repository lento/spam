# -*- coding: utf-8 -*-
"""Project tabs controllers"""

from tg import expose, request, tmpl_context
from pylons.i18n import ugettext as _, lazy_ugettext as l_
from repoze.what import predicates

from spam.lib.base import SPAMBaseController
from spam.model import project_get_eager


class TabController(SPAMBaseController):
    """The controller for shot tabs."""
    def __before__(self, *args, **kw):
        proj, sc, sh = request.url.split('/')[-5:-2]
        project = project_get_eager(proj)
        tmpl_context.project = project
        scene = [s for s in project.scenes if s.name==sc][0]
        tmpl_context.scene = scene
        shot = [s for s in scene.shots if s.name==sh][0]
        tmpl_context.shot = shot

    @expose('spam.templates.shot.tabs.summary')
    def summary(self):
        """Handle the 'summary' tab."""
        #project = tmpl_context.project
        return dict()

    @expose('spam.templates.shot.tabs.assets')
    def assets(self):
        """Handle the 'assets' tab."""
        #project = tmpl_context.project
        return dict()

    @expose('spam.templates.shot.tabs.tasks')
    def tasks(self):
        """Handle the 'tasks' tab."""
        #project = tmpl_context.project
        return dict()


