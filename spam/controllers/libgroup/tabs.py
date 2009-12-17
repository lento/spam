# -*- coding: utf-8 -*-
"""Libgroup tabs controllers"""

from tg import expose, request, tmpl_context, require
from pylons.i18n import ugettext as _, lazy_ugettext as l_
from repoze.what import predicates

from spam.lib.base import SPAMBaseController
from spam.model import libgroup_get
from spam.lib.predicates import is_project_user

class TabController(SPAMBaseController):
    """The controller for libgroup tabs."""
    def _before(self, *args, **kw):
        proj, libgroup_id = request.url.split('/')[-4:-2]
        libgroup = libgroup_get(proj, libgroup_id)
        tmpl_context.project = libgroup.project
        tmpl_context.libgroup = libgroup

    @require(is_project_user())
    @expose('spam.templates.libgroup.tabs.summary')
    def summary(self):
        """Handle the 'summary' tab."""
        return dict()

    @require(is_project_user())
    @expose('spam.templates.libgroup.tabs.tasks')
    def tasks(self):
        """Handle the 'tasks' tab."""
        return dict()


