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
"""Tag controller"""

from tg import expose, url, tmpl_context, redirect, validate, require
from tg.controllers import RestController
from pylons.i18n import ugettext as _, ungettext as n_, lazy_ugettext as l_
from spam.model import session_get, taggable_get, tag_get, Tag
from spam.lib.widgets import FormTagNew, FormTagConfirm, FormTagRemove
#from spam.lib.widgets import BoxTags
from spam.lib.notifications import notify, TOPIC_TAGS
from spam.lib.journaling import journal
from repoze.what.predicates import in_group

import logging
log = logging.getLogger(__name__)

# form widgets
f_new = FormTagNew(action=url('/tag'))
f_confirm = FormTagConfirm(action=url('/tag'))
f_remove = FormTagRemove(action=url('/tag'))

# live widgets
#b_tags = BoxTags()

class Controller(RestController):
    """REST controller for managing tags.
    
    In addition to the standard REST verbs this controller defines the following
    REST-like methods:
        * ``remove``  (:meth:`remove`)
    """
    
    @require(in_group('administrators'))
    @expose('spam.templates.tags.get_all')
    def get_all(self, taggable_id):
        """Return a html fragment with a list of tags for this object."""
#        tmpl_context.b_tags = b_tags
        taggable = taggable_get(taggable_id)
        return dict(tags=taggable.tags)

    @expose('spam.templates.tags.get_all')
    def _default(self, taggable_id, *args, **kwargs):
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
        session = session_get()
        taggable = taggable_get(taggable_id)
        
        f_new.value = dict(taggable_id=taggable.id,
                       current_tags_=', '.join([t.id for t in taggable.tags]),
                      )
        
        tags = session.query(Tag).order_by('id')
        choices = [t.id for t in tags if t not in taggable.tags]
        f_new.child.children.tagids.options = choices
        tmpl_context.form = f_new
        return dict(title='%s %s' % (_('Add tags to:'), taggable.tagged.path))

    @require(in_group('administrators'))
    @expose('json')
    @expose('spam.templates.forms.result')
    @validate(f_new, error_handler=new)
    def post(self, taggable_id, tagids=[], new_tags=None):
        """Add tags to a ``taggable`` obect."""
        session = session_get()
        user = tmpl_context.user
        taggable = taggable_get(taggable_id)

        if isinstance(tagids, list):
            tags = [tag_get(i) for i in tagids]
        else:
            tags = [tag_get(tagids)]

        if new_tags:
            tags.extend([tag_get(name) for name in new_tags.split(', ')])

        added_tags = []
        updates = []
        for tag in tags:
            if tag not in taggable.tags:
                taggable.tags.append(tag)
                added_tags.append(tag)

                # prepare updates to notify clients
                updates.append(dict(item=tag, type='added', topic=TOPIC_TAGS,
                                                            filter=taggable_id))

        if added_tags:
            added = ', '.join([t.id for t in added_tags])
            msg = '%s %s %s' % (added,
                                n_('tag added to:',
                                   'tags added to:', len(added_tags)),
                                taggable_id)
            status = 'ok'

            # notify clients
            notify.send(updates)

            # log into Journal
            journal.add(user, '%s - %s' % (msg, taggable.tagged))
        else:
            msg = _('No new tag applied')
            status = 'info'

        return dict(msg=msg, status=status, updates=updates)

    @require(in_group('administrators'))
    @expose('spam.templates.forms.form')
    def get_delete(self, tag_id, **kwargs):
        """Display a DELETE confirmation form."""
        tag = tag_get(tag_id)
        f_confirm.custom_method = 'DELETE'
        f_confirm.value = dict(tag_id=tag.id)
        tmpl_context.form = f_confirm
        return dict(title='%s %s?' % (_('Are you sure you want to delete tag:'),
                                                                        tag.id))

    @require(in_group('administrators'))
    @expose('json')
    @expose('spam.templates.forms.result')
    @validate(f_confirm, error_handler=get_delete)
    def post_delete(self, tag_id):
        """Delete a tag."""
        session = session_get()
        user = tmpl_context.user
        tag = tag_get(tag_id)

        session.delete(tag)

        msg = '%s %s' % (_('Deleted tag:'), tag.id)

        # log into Journal
        journal.add(user, '%s - %s' % (msg, tag))
        
        # notify clients
        updates = [dict(item=tag, type='deleted', topic=TOPIC_TAGS)]
        notify.send(updates)

        return dict(msg=msg, status='ok', updates=updates)

    # Custom REST-like actions
    _custom_actions = ['remove']

    @require(in_group('administrators'))
    @expose('json')
    @expose('spam.templates.forms.result')
    @validate(f_remove)
    def remove(self, taggable_id, tagids=[]):
        """Remove tags from an object."""
        session = session_get()
        user = tmpl_context.user
        taggable = taggable_get(taggable_id)

        if isinstance(tagids, list):
            tags = [tag_get(i) for i in tagids]
        else:
            tags = [tag_get(tagids)]

        removed_tags = []
        updates = []
        for tag in tags:
            if tag in taggable.tags:
                taggable.tags.remove(tag)
                removed_tags.append(tag)

                # prepare updates
                updates.append(dict(item=tag, type='deleted', topic=TOPIC_TAGS,
                                                            filter=taggable_id))

        if removed_tags:
            removed = ', '.join([t.id for t in removed_tags])
            msg = '%s %s %s' % (removed,
                                n_('tag removed from:',
                                   'tags removed from:', len(removed_tags)),
                                taggable_id)
            status = 'ok'

            # notify clients
            notify.send(updates)

            # log into Journal
            journal.add(user, '%s - %s' % (msg, taggable.tagged))
        else:
            msg = _('No tag removed')
            status = 'info'

        return dict(msg=msg, status=status, updates=updates)

