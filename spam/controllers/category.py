from tg import expose, url, tmpl_context, redirect, validate, require
from tg.controllers import RestController
from pylons.i18n import ugettext as _, lazy_ugettext as l_
from spam.model import session_get, Category, category_get
from spam.lib.widgets import FormCategoryNew, FormCategoryEdit
from spam.lib.widgets import FormCategoryConfirm, TableCategories
from spam.lib.notifications import notify
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
    
    @require(in_group('administrators'))
    @expose('spam.templates.category.get_all')
    def get_all(self):
        tmpl_context.t_categories = t_categories
        query = session_get().query(Category)
        categories = query.order_by('ordering', 'name')
        return dict(page='admin/categories', sidebar=('admin', 'categories'),
                                                        categories=categories)

    @require(in_group('administrators'))
    @expose('json')
    @expose('spam.templates.category.get_one')
    def get_one(self, name):
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
    def post(self, name, **kwargs):
        """Create a new category"""
        session = session_get()
        
        # add category to shared db
        category = Category(name=name)
        session.add(category)
        
        # send a stomp message to notify clients
        notify.send(category, update_type='added')
        return dict(msg='created category "%s"' % name, result='success')
    
    @require(in_group('administrators'))
    @expose('spam.templates.forms.form')
    def edit(self, name, **kwargs):
        """Display a EDIT form."""
        tmpl_context.form = f_edit
        category = category_get(name)
        fargs = dict(category_id=category.id, name=category.name)
        fcargs = dict()
        return dict(title='Edit category "%s"' % category.name, args=fargs,
                                                            child_args=fcargs)
        
    @require(in_group('administrators'))
    @expose('json')
    @expose('spam.templates.forms.result')
    @validate(f_edit, error_handler=edit)
    def put(self, category_id, name, **kwargs):
        """Edit a category"""
        category = category_get(category_id)
        category.name = name
        notify.send(category, update_type='updated')
        return dict(msg='updated category "%s"' % name, result='success')

    @require(in_group('administrators'))
    @expose('spam.templates.forms.form')
    def get_delete(self, category_id, **kwargs):
        """Display a DELETE confirmation form."""
        tmpl_context.form = f_confirm
        category = category_get(category_id)
        fargs = dict(_method='DELETE', category_id=category.id,
                     name_=category.name)
        fcargs = dict()
        warning = ('This will delete the category entry in the database. '
                   'All the assets in this category will be orphaned.')
        return dict(
                title='Are you sure you want to delete "%s"?' % category.name,
                warning=warning, args=fargs, child_args=fcargs)

    @require(in_group('administrators'))
    @expose('json')
    @expose('spam.templates.forms.result')
    @validate(f_confirm, error_handler=get_delete)
    def post_delete(self, category_id, **kwargs):
        """Delete a category.
        
        Only delete the category record from the common db, all the assets
        in this category will be orphaned, and must be removed manually.
        """
        session = session_get()
        category = category_get(category_id)
        session.delete(category)
        notify.send(category, update_type='deleted')
        return dict(msg='deleted category "%s"' % category.name,
                                                            result='success')
    
    # Custom REST-like actions
    custom_actions = []

