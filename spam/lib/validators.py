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
"""Custom form validators for SPAM."""

import re
from pylons.i18n import ugettext as _, lazy_ugettext as l_
from formencode.api import Invalid
from formencode.schema import format_compound_error
import tw2.core as twc
from spam.model import category_get
from spam.lib.exceptions import SPAMDBError, SPAMDBNotFound


class CategoryNamingConvention(twc.Validator):
    """Confirm an asset name matches the naming convention for its category.

    `category_field`
        Name of the sibling field this must match
    """
    msgs = {
        'mismatch': "Must match category naming convention: $naming_convention",
        'nocategory': "Invalid category"
    }

    def __init__(self, category_field, **kw):
        super(CategoryNamingConvention, self).__init__(**kw)
        self.category_field = category_field

    def validate_python(self, value, state):
        super(CategoryNamingConvention, self).validate_python(value, state)

        categoryid = state[self.category_field]
        if not isinstance(categoryid, basestring):
            raise twc.ValidationError('nocategory', self)

        try:
            category = category_get(categoryid)
            self.naming_convention = category.naming_convention
        except SPAMDBError, SPAMDBNotFound:
            raise twc.ValidationError('nocategory', self)

        if not re.match(self.naming_convention, value):
            raise twc.ValidationError('mismatch', self)

