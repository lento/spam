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
from tw.forms.validators import FormValidator
from spam.model import category_get

class CategoryNamingConvention(FormValidator):
    """Validate an asset name against the naming convention for its category."""

    category_field = None
    name_field = None
    __unpackargs__ = ('category_field', 'name_field')
    
    messages = {
        'notDict': _("Fields should be a dictionary"),
        }

    def validate_partial(self, field_dict, state):
        if self.category_field not in field_dict:
            return
        if self.name_field not in field_dict:
            return
        self.validate_python(field_dict, state)

    def validate_python(self, field_dict, state):
        try:
            category_id = field_dict[self.category_field]
            asset_name = field_dict[self.name_field]
        except TypeError:
            # Generally because field_dict isn't a dict
            raise Invalid(self.message('notDict', state), field_dict, state)

        category = category_get(category_id)
        if not re.match(category.naming_convention, asset_name):
            errors = dict(name='name does not follow naming convention for '
                            'this category (%s)' % category.naming_convention)
            raise Invalid(format_compound_error(errors),
                          field_dict, state, error_dict=errors)

