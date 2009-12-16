import re
from pylons.i18n import ugettext as _, lazy_ugettext as l_
from formencode.api import Invalid
from formencode.schema import format_compound_error
from tw.forms.validators import FormValidator
from spam.model import category_get

class CategoryNamingConvention(FormValidator):
    """
    """

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
            category_name = field_dict[self.category_field]
            asset_name = field_dict[self.name_field]
        except TypeError:
            # Generally because field_dict isn't a dict
            raise Invalid(self.message('notDict', state), field_dict, state)

        category = category_get(category_name)
        if not re.match(category.naming_convention, asset_name):
            errors = dict(name='name does not follow naming convention for '
                            'this category (%s)' % category.naming_convention)
            raise Invalid(format_compound_error(errors),
                          field_dict, state, error_dict=errors)

