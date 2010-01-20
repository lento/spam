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
"""Scene tabs"""

from tg import expose, request, tmpl_context, require
from pylons.i18n import ugettext as _, lazy_ugettext as l_
from repoze.what import predicates

from spam.lib.base import SPAMBaseController
from spam.model import scene_get
from spam.lib.predicates import is_project_user
from spam.lib.widgets import ListTags, TableNotes, BoxShotsStatus

# live widgets
b_shots_status = BoxShotsStatus()
l_tags = ListTags()
t_notes = TableNotes()

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
        """Handle the 'summary' tab.
        
        This tab offers a quick view on the current status of the scene.
        """
        tmpl_context.b_shots_status = b_shots_status
        tmpl_context.l_tags = l_tags
        tmpl_context.t_notes = t_notes
        scene = tmpl_context.scene
        return dict()

