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
"""Category controller"""

from tg import expose, url, tmpl_context, redirect, validate, require
from tg.controllers import RestController
from pylons.i18n import ugettext as _, lazy_ugettext as l_
from spam.model import session_get, Category, category_get, diff_dicts
from spam.lib.widgets import FormCategoryNew, FormCategoryEdit
from spam.lib.widgets import FormCategoryConfirm, TableCategories
from spam.lib.notifications import notify, TOPIC_CATEGORIES
from spam.lib.journaling import journal
from repoze.what.predicates import in_group

import logging
log = logging.getLogger(__name__)

# form widgets
f_new = FormCategoryNew(action=url('/category'))
f_edit = FormCategoryEdit(action=url('/category'))
f_confirm = FormCategoryConfirm(action=url('/category'))

# livetable widgets
t_categories = TableCategories(id='t_categories')

class Controller(RestController):
    """REST controller for managing categories."""
    
    @require(in_group('administrators'))
    @expose('spam.templates.category.get_all')
    def get_all(self):
        """Return a `full` page with a list of all categories and a button to
        add new categories."""
        query = session_get().query(Category)
        categories = query.order_by('ordering', 'id')

        t_categories.value = categories.all()
        tmpl_context.t_categories = t_categories
        return dict(page='admin/categories', sidebar=('admin', 'categories'))

    @require(in_group('administrators'))
    @expose('json')
    @expose('spam.templates.category.get_one')
    def get_one(self, name):
        """This method is currently unused, but is needed for the 
        RESTController to work."""
        category = category_get(name)
        return dict(category=category)

    @require(in_group('administrators'))
    @expose('spam.templates.forms.form')
    def new(self, **kwargs):
        """Display a NEW form."""
        tmpl_context.form = f_new
        return dict(title=_('Create a new category'))

    @require(in_group('administrators'))
    @expose('json')
    @expose('spam.templates.forms.result')
    @validate(f_new, error_handler=new)
    def post(self, category_id, ordering=None, naming_convention=None):
        """Create a new category"""
        session = session_get()
        user = tmpl_context.user

        # add category to shared db
        category = Category(category_id, ordering=ordering,
                                            naming_convention=naming_convention)
        session.add(category)

        msg = '%s %s' % (_('Created category:'), category_id)

        # log into Journal
        journal.add(user, '%s - %s' % (msg, category))

        # notify clients
        updates = [dict(item=category, type='added', topic=TOPIC_CATEGORIES)]
        notify.send(updates)

        return dict(msg=msg, status='ok', updates=updates)
    
    @require(in_group('administrators'))
    @expose('spam.templates.forms.form')
    def edit(self, category_id, **kwargs):
        """Display a EDIT form."""
        category = category_get(category_id)
        f_edit.value = dict(category_id=category.id,
                            id_=category.id,
                            ordering=category.ordering,
                            naming_convention=category.naming_convention)
        tmpl_context.form = f_edit
        return dict(title='%s %s' % (_('Edit category:'), category.id))
        
    @require(in_group('administrators'))
    @expose('json')
    @expose('spam.templates.forms.result')
    @validate(f_edit, error_handler=edit)
    def put(self, category_id, ordering=None, naming_convention=None):
        """Edit a category"""
        session = session_get()
        user = tmpl_context.user
        category = category_get(category_id)
        old = category.__dict__.copy()

        modified = False
        if ordering is not None and not ordering == category.ordering:
            category.ordering = ordering
            modified = True

        if (naming_convention is not None and
                        not naming_convention == category.naming_convention):
            category.naming_convention = naming_convention
            modified = True

        if modified:
            new = category.__dict__.copy()

            msg = '%s %s' % (_('Updated category:'), category_id)

            # log into Journal
            journal.add(user, '%s - %s' % (msg, diff_dicts(old, new)))

            # notify clients
            updates = [
                dict(item=category, type='updated', topic=TOPIC_CATEGORIES)
                ]
            notify.send(updates)

            return dict(msg=msg, status='ok', updates=updates)

        return dict(msg='%s %s' % (_('Category is unchanged:'), category_id),
                                                    status='info', updates=[])

    @require(in_group('administrators'))
    @expose('spam.templates.forms.form')
    def get_delete(self, category_id, **kwargs):
        """Display a DELETE confirmation form."""
        category = category_get(category_id)
        f_confirm.custom_method = 'DELETE'
        f_confirm.value = dict(category_id=category.id,
                               id_=category.id,
                               ordering_=str(category.ordering),
                               naming_convention_=category.naming_convention)
        warning = ('This will delete the category entry in the database. '
                   'All the assets in this category will be orphaned.')
        tmpl_context.form = f_confirm
        return dict(title='%s %s?' % (_('Are you sure you want to delete:'),
                                                category.id), warning=warning)

    @require(in_group('administrators'))
    @expose('json')
    @expose('spam.templates.forms.result')
    @validate(f_confirm, error_handler=get_delete)
    def post_delete(self, category_id):
        """Delete a category.

        Only delete the category record from the common db, all the assets
        in this category will be orphaned, and must be removed manually.
        """
        session = session_get()
        user = tmpl_context.user
        category = category_get(category_id)
        session.delete(category)

        msg = '%s %s' % (_('Deleted category:'), category.id)

        # log into Journal
        journal.add(user, '%s - %s' % (msg, category))

        # notify clients
        updates = [dict(item=category, type='deleted', topic=TOPIC_CATEGORIES)]
        notify.send(updates)

        return dict(msg=msg, status='ok', updates=updates)

    # Custom REST-like actions
    _custom_actions = []

