# -*- coding: utf-8 -*-
"""Scene tabs controllers"""

from tg import expose, request, tmpl_context, require
from pylons.i18n import ugettext as _, lazy_ugettext as l_
from repoze.what import predicates

from spam.lib.base import SPAMBaseController
from spam.model import scene_get
from spam.lib.predicates import is_project_user

class TabController(SPAMBaseController):
    """The controller for scene tabs."""
    def _before(self, *args, **kw):
        proj, sc = request.url.split('/')[-4:-2]
        scene = scene_get(proj, sc)
        tmpl_context.project = scene.project
        tmpl_context.scene = scene

    @require(is_project_user())
    @expose('spam.templates.scene.tabs.summary')
    def summary(self):
        """Handle the 'summary' tab."""
        return dict()

    @require(is_project_user())
    @expose('spam.templates.scene.tabs.tasks')
    def tasks(self):
        """Handle the 'tasks' tab."""
        return dict()


