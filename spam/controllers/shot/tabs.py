# -*- coding: utf-8 -*-
#
# This file is part of SPAM (Spark Project & Asset Manager).
#
# SPAM is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# SPAM is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with SPAM.  If not, see <http://www.gnu.org/licenses/>.
#
# Original Copyright (c) 2010, Lorenzo Pierfederici <lpierfederici@gmail.com>
# Contributor(s): 
#
"""Shot tabs"""

from tg import expose, request, tmpl_context, require
from pylons.i18n import ugettext as _, lazy_ugettext as l_
from repoze.what import predicates

from spam.lib.base import SPAMBaseController
from spam.model import scene_get, shot_get
from spam.lib.predicates import is_project_user
from spam.lib.widgets import TableNotes
#from spam.lib.widgets import BoxTags, BoxCategoriesStatus

# live widgets
#b_categories_status = BoxCategoriesStatus()
#b_tags = BoxTags()
t_notes = TableNotes()

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
        """Handle the 'summary' tab.
        
        This tab offers a quick view on the current status of the shot.
        """
        project = tmpl_context.project
        user = tmpl_context.user
        shot = tmpl_context.shot

#        tmpl_context.b_categories_status = b_categories_status
#        tmpl_context.b_tags = b_tags
        tmpl_context.t_notes = t_notes
#        cat_extra_data = dict(proj_id=shot.proj_id, container_type='shot',
#                                                        container_id=shot.id)
#        tag_extra_data = dict(taggable_id=shot.id, user_id=user.user_id,
#                                                                project=project)
        note_extra_data = dict(user_id=user.user_id)
        return dict(note_extra_data=note_extra_data)

