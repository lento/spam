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
"""Category controller"""

from tg import expose, url, tmpl_context, redirect, validate, require
from tg.controllers import RestController
from pylons.i18n import ugettext as _, lazy_ugettext as l_
from spam.model import session_get, Category, category_get, diff_dicts
from spam.lib.widgets import FormCategoryNew, FormCategoryEdit
from spam.lib.widgets import FormCategoryConfirm, TableCategories
from spam.lib.notifications import notify
from spam.lib.journaling import journal
from repoze.what.predicates import in_group

import logging
log = logging.getLogger(__name__)

# form widgets
f_new = FormCategoryNew(action=url('/category/'))
f_edit = FormCategoryEdit(action=url('/category/'))
f_confirm = FormCategoryConfirm(action=url('/category/'))

# livetable widgets
t_categories = TableCategories()

class Controller(RestController):
    """REST controller for managing categories"""
    
    @require(in_group('administrators'))
    @expose('spam.templates.category.get_all')
    def get_all(self):
        """Return a `full` page with a list of all categories and a button to
        add new categories."""
        tmpl_context.t_categories = t_categories
        query = session_get().query(Category)
        categories = query.order_by('ordering', 'id')
        return dict(page='admin/categories', sidebar=('admin', 'categories'),
                                                        categories=categories)

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
        fargs = dict()
        fcargs = dict()
        return dict(title='Create a new category', args=fargs,
                                                            child_args=fcargs)

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
        
        # log into Journal
        journal.add(user, 'created %s' % category)
        
        # send a stomp message to notify clients
        notify.send(category, update_type='added')
        return dict(msg='created category "%s"' % category_id, result='success')
    
    @require(in_group('administrators'))
    @expose('spam.templates.forms.form')
    def edit(self, category_id, **kwargs):
        """Display a EDIT form."""
        tmpl_context.form = f_edit
        category = category_get(category_id)
        fargs = dict(category_id=category.id, id_=category.id,
                     ordering=category.ordering,
                     naming_convention=category.naming_convention)
        fcargs = dict()
        return dict(title='Edit category "%s"' % category.id, args=fargs,
                                                            child_args=fcargs)
        
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
        if ordering:
            category.ordering = ordering
            modified = True
        
        if naming_convention:
            category.naming_convention = naming_convention
            modified = True
        
        if modified:
            new = category.__dict__.copy()
            
            # log into Journal
            journal.add(user, 'modified %s: %s' %
                                            (category, diff_dicts(old, new)))
        
            # send a stomp message to notify clients
            notify.send(category, update_type='updated')
            return dict(msg='updated category "%s"' %
                                                category_id, result='success')
        return dict(msg='category "%s" unchanged' %
                                                category_id, result='success')

    @require(in_group('administrators'))
    @expose('spam.templates.forms.form')
    def get_delete(self, category_id, **kwargs):
        """Display a DELETE confirmation form."""
        tmpl_context.form = f_confirm
        category = category_get(category_id)
        fargs = dict(_method='DELETE', category_id=category.id,
                     id_=category.id,
                     ordering_=category.ordering,
                     naming_convention_=category.naming_convention)
        fcargs = dict()
        warning = ('This will delete the category entry in the database. '
                   'All the assets in this category will be orphaned.')
        return dict(
                title='Are you sure you want to delete "%s"?' % category.id,
                warning=warning, args=fargs, child_args=fcargs)

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

        # log into Journal
        journal.add(user, 'deleted %s' % category)
        
        # send a stomp message to notify clients
        notify.send(category, update_type='deleted')
        return dict(msg='deleted category "%s"' % category.id,
                                                            result='success')
    
    # Custom REST-like actions
    custom_actions = []

