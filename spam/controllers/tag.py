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
"""Tag controller"""

from tg import expose, url, tmpl_context, redirect, validate, require
from tg.controllers import RestController
from pylons.i18n import ugettext as _, lazy_ugettext as l_
from spam.model import session_get, taggable_get, tag_get, Tag
from spam.lib.widgets import FormTagNew, FormTagConfirm, FormTagRemove
from spam.lib.widgets import ListTags
from spam.lib.notifications import notify
from spam.lib.journaling import journal
from repoze.what.predicates import in_group

import logging
log = logging.getLogger(__name__)

# form widgets
f_new = FormTagNew(action=url('/tag/'))
f_confirm = FormTagConfirm(action=url('/tag/'))
f_remove = FormTagRemove(action=url('/tag/'))

# live widgets
l_tags = ListTags()

class Controller(RestController):
    """REST controller for managing tags"""
    
    @require(in_group('administrators'))
    @expose('spam.templates.tags.get_all')
    def get_all(self, taggable_id):
        """Return a html fragment with a list of tags for this object."""
        tmpl_context.l_tags = l_tags
        taggable = taggable_get(taggable_id)
        return dict(tags=taggable.tags)

    @expose('spam.templates.tags.get_all')
    def default(self, taggable_id, *args, **kwargs):
        """Catch request to `tag/<something>' and pass them to :meth:`get_all`,
        because RESTController doesn't dispatch to get_all when there are
        arguments.
        """
        return self.get_all(taggable_id)

    @require(in_group('administrators'))
    @expose('json')
    @expose('spam.templates.tags.get_one')
    def get_one(self, taggable_id, tag_id):
        """This method is currently unused, but is needed for the 
        RESTController to work."""
        tag = tag_get(tag_id)
        return dict(tag=tag)

    @require(in_group('administrators'))
    @expose('spam.templates.forms.form')
    def new(self, taggable_id, **kwargs):
        """Display a NEW form."""
        tmpl_context.form = f_new
        session = session_get()
        taggable = taggable_get(taggable_id)
        
        fargs = dict(taggable_id=taggable.id,
                     current_tags_=', '.join([t.id for t in taggable.tags]),
                    )
        
        tags = session.query(Tag).order_by('id')
        choices = [t.id for t in tags if t not in taggable.tags]
        fcargs = dict(tag_ids=dict(options=choices))
        return dict(title='Add a tag to "%s"' % taggable.tagged.path,
                                                args=fargs, child_args=fcargs)
    
    @require(in_group('administrators'))
    @expose('json')
    @expose('spam.templates.forms.result')
    @validate(f_new, error_handler=new)
    def post(self, taggable_id, tag_ids=[], new_tags=None, **kwargs):
        """Add tags to a ``taggable`` obect."""
        session = session_get()
        user = tmpl_context.user
        taggable = taggable_get(taggable_id)
        
        tags = [tag_get(i) for i in tag_ids]
        if new_tags:
            tags.extend([tag_get(name) for name in new_tags.split(', ')])
        
        added_tags = []
        for tag in tags:
            if tag not in taggable.tags:
                taggable.tags.append(tag)
                added_tags.append(tag.id)
        added_tags = ', '.join(added_tags)
        
        # log into Journal
        journal.add(user, 'added tag(s) "%s" to %s' %
                                            (added_tags, taggable.tagged))
        
        # send a stomp message to notify clients
        #notify.send(tag, update_type='added', shot=shot)
        return dict(msg='added tag(s) "%s" to %s' % 
                       (added_tags, taggable.tagged.path), result='success')
    
    @require(in_group('administrators'))
    @expose('spam.templates.forms.form')
    def get_delete(self, tag_id, **kwargs):
        """Display a DELETE confirmation form."""
        tmpl_context.form = f_confirm
        tag = tag_get(tag_id)
        fargs = dict(_method='DELETE', tag_id=tag.id)
        fcargs = dict()
        #warning = ('This will delete the category entry in the database. '
        #           'All the assets in this category will be orphaned.')
        return dict(
                title='Are you sure you want to delete tag "%s"?' % tag.id,
                warning=warning, args=fargs, child_args=fcargs)

    @require(in_group('administrators'))
    @expose('json')
    @expose('spam.templates.forms.result')
    @validate(f_confirm, error_handler=get_delete)
    def post_delete(self, tag_id, **kwargs):
        """Delete a tag."""
        session = session_get()
        user = tmpl_context.user
        tag = tag_get(tag_id)
        
        session.delete(tag)
        
        # log into Journal
        journal.add(user, 'deleted %s' % tag)
        
        # send a stomp message to notify clients
        #notify.send(tag, update_type='deleted')
        return dict(msg='deleted tag "%s"' % tag.id, result='success')
    
    # Custom REST-like actions
    custom_actions = ['remove']
    
    @require(in_group('administrators'))
    @expose('spam.templates.forms.form')
    def get_remove(self, taggable_id, **kwargs):
        """Display a REMOVE tag form."""
        tmpl_context.form = f_remove
        taggable = taggable_get(taggable_id)
        fargs = dict(taggable_id=taggable.id)
        choices = [t.id for t in taggable.tags]
        fcargs = dict(tag_ids=dict(options=choices))
        return dict(title='Remove tags from "%s"' % taggable.tagged.path,
                                                args=fargs, child_args=fcargs)

    @require(in_group('administrators'))
    @expose('json')
    @expose('spam.templates.forms.result')
    @validate(f_remove, error_handler=get_remove)
    def post_remove(self, taggable_id, tag_ids=[], **kwargs):
        """Delete a tag."""
        session = session_get()
        user = tmpl_context.user
        taggable = taggable_get(taggable_id)
        
        tags = [tag_get(i) for i in tag_ids]
        removed_tags = []
        for tag in tags:
            if tag in taggable.tags:
                taggable.tags.remove(tag)
                removed_tags.append(tag.id)
        removed_tags = ', '.join(removed_tags)
        
        # log into Journal
        journal.add(user, 'removed tag(s) "%s" from %s' %
                                        (removed_tags, taggable.tagged))
        
        # send a stomp message to notify clients
        #notify.send(tag, update_type='removed', taggable=taggable)
        return dict(msg='removed tag(s) "%s" from %s' %
                        (removed_tags, taggable.tagged.path), result='success')

