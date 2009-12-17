# -*- coding: utf-8 -*-
"""Shot tabs controllers"""

from tg import expose, request, tmpl_context, require
from pylons.i18n import ugettext as _, lazy_ugettext as l_
from repoze.what import predicates

from spam.lib.base import SPAMBaseController
from spam.model import scene_get, shot_get
from spam.lib.predicates import is_project_user

class TabController(SPAMBaseController):
    """The controller for shot tabs."""
    def _before(self, *args, **kw):
        proj, sc, sh = request.url.split('/')[-5:-2]
        shot = shot_get(proj, sc, sh)
        tmpl_context.project = shot.project
        tmpl_context.scene = shot.parent
        tmpl_context.shot = shot

    @require(is_project_user())
    @expose('spam.templates.shot.tabs.summary')
    def summary(self):
        """Handle the 'summary' tab."""
        return dict()

    @require(is_project_user())
    @expose('spam.templates.shot.tabs.assets')
    def assets(self):
        """Handle the 'assets' tab."""
        return dict()

    @require(is_project_user())
    @expose('spam.templates.shot.tabs.tasks')
    def tasks(self):
        """Handle the 'tasks' tab."""
        return dict()


