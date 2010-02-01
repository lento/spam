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
"""Libgroup tabs"""

from tg import expose, request, tmpl_context, require
from pylons.i18n import ugettext as _, lazy_ugettext as l_
from repoze.what import predicates

from spam.lib.base import SPAMBaseController
from spam.model import libgroup_get
from spam.lib.predicates import is_project_user
from spam.lib.widgets import BoxTags, TableNotes, BoxLibgroupsStatus
from spam.lib.widgets import BoxCategoriesStatus
# live widgets
b_libgroups_status = BoxLibgroupsStatus()
b_categories_status = BoxCategoriesStatus()
b_tags = BoxTags()
t_notes = TableNotes()

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
        """Handle the 'summary' tab.
        
        This tab offers a quick view on the current status of the libgroup.
        """
        project = tmpl_context.project
        user = tmpl_context.user
        libgroup = tmpl_context.libgroup
        tmpl_context.b_libgroups_status = b_libgroups_status
        tmpl_context.b_categories_status = b_categories_status
        tmpl_context.b_tags = b_tags
        tmpl_context.t_notes = t_notes
        cat_extra_data = dict(proj_id=libgroup.proj_id,
                            container_type='libgroup', container_id=libgroup.id)
        tag_extra_data = dict(taggable_id=libgroup.id, user_id=user.user_id,
                                                                project=project)
        note_extra_data = dict(user_id=user.user_id)
        return dict(cat_extra_data=cat_extra_data,
                note_extra_data=note_extra_data, tag_extra_data=tag_extra_data)


