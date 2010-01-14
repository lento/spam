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
"""Journal controller"""

from tg import expose, url, tmpl_context, require
from tg.decorators import paginate
from pylons.i18n import ugettext as _, lazy_ugettext as l_
from sqlalchemy import desc
from spam.lib.base import SPAMBaseController
from spam.model import session_get, Journal
from spam.lib.widgets import TableJournal
from repoze.what.predicates import not_anonymous

import logging
log = logging.getLogger(__name__)

# livetable widgets
t_journal = TableJournal()

class Controller(SPAMBaseController):
    """Controller for the journal"""
    
    @require(not_anonymous())
    @expose('spam.templates.journal')
    @paginate('journal', items_per_page=30)
    def index(self):
        """Return a `full` page with a table of journal entries."""
        tmpl_context.t_journal = t_journal
        query = session_get().query(Journal)
        journal = query.order_by(desc('created'))
        return dict(page='user/journal', sidebar=('user', 'journal'),
                                                                journal=journal)


