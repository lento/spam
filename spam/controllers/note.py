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
"""Note controller"""

from tg import expose, url, tmpl_context, redirect, validate, require
from tg.controllers import RestController
from pylons.i18n import ugettext as _, lazy_ugettext as l_
from spam.model import session_get, annotable_get, note_get, Note, AssetVersion
from spam.lib.widgets import FormNoteNew, FormNoteConfirm
from spam.lib.widgets import TableNotes
from spam.lib.notifications import notify
from repoze.what.predicates import in_group
from spam.lib.decorators import project_set_active
from spam.lib.predicates import is_project_user, is_project_admin

import logging
log = logging.getLogger(__name__)

# form widgets
f_new = FormNoteNew(action=url('/note/'))
f_confirm = FormNoteConfirm(action=url('/note/'))

# live widgets
t_notes = TableNotes()

class Controller(RestController):
    """REST controller for managing notes"""
    
    @project_set_active
    @require(is_project_user())
    @expose('spam.templates.notes.get_all')
    def get_all(self, proj, annotable_id):
        """Return a html fragment with a list of notes for this object."""
        tmpl_context.t_notes = t_notes
        annotable = annotable_get(annotable_id)
        return dict(notes=annotable.notes, annotable_id=annotable.id)

    @project_set_active
    @require(is_project_user())
    @expose('spam.templates.notes.get_all')
    def default(self, proj, annotable_id, *args, **kwargs):
        """Catch request to `note/<something>' and pass them to :meth:`get_all`,
        because RESTController doesn't dispatch to get_all when there are
        arguments.
        """
        return self.get_all(proj, annotable_id)

    @project_set_active
    @require(is_project_user())
    @expose('json')
    @expose('spam.templates.notes.get_one')
    def get_one(self, proj, annotable_id, note_id):
        """This method is currently unused, but is needed for the 
        RESTController to work."""
        note = note_get(note_id)
        return dict(note=note)

    @project_set_active
    @require(is_project_user())
    @expose('spam.templates.forms.form')
    def new(self, proj, annotable_id, **kwargs):
        """Display a NEW form."""
        project = tmpl_context.project
        tmpl_context.form = f_new
        session = session_get()
        annotable = annotable_get(annotable_id)
        
        fargs = dict(proj=project.id, annotable_id=annotable.id)
        fcargs = dict()
        return dict(title='Add a note to "%s"' % annotable.annotated.path,
                                                args=fargs, child_args=fcargs)
    
    @project_set_active
    @require(is_project_user())
    @expose('json')
    @expose('spam.templates.forms.result')
    @validate(f_new, error_handler=new)
    def post(self, proj, annotable_id, text):
        """Add notes to a ``annotable`` obect."""
        session = session_get()
        user = tmpl_context.user
        annotable = annotable_get(annotable_id)
        ob = annotable.annotated
        
        note = Note(user, text)
        annotable.notes.append(note)
        session.refresh(annotable)
        
        notify.send(note, update_type='added', annotable_id=ob.annotable.id)
        if isinstance(ob, AssetVersion):
            notify.send(ob.asset)
        else:
            notify.send(ob)
        return dict(msg='added note to "%s"' % annotable.annotated.path,
                                                    result='success', note=note)
    
    @project_set_active
    @require(is_project_admin())
    @expose('spam.templates.forms.form')
    def get_delete(self, proj, note_id, **kwargs):
        """Display a DELETE confirmation form."""
        project = tmpl_context.project
        tmpl_context.form = f_confirm
        note = note_get(note_id)
        fargs = dict(_method='DELETE', proj=project.id, note_id=note.id,
                                                                text_=note.text)
        fcargs = dict()
        return dict(
                title='Are you sure you want to delete note "%s"?' % note.id,
                warning=warning, args=fargs, child_args=fcargs)

    @project_set_active
    @require(is_project_admin())
    @expose('json')
    @expose('spam.templates.forms.result')
    @validate(f_confirm, error_handler=get_delete)
    def post_delete(self, proj, note_id):
        """Delete a note."""
        session = session_get()
        note = note_get(note_id)
        ob = note.annotated
        
        session.delete(note)
        session.refresh(ob.annotable)
        
        notify.send(note, update_type='deleted', annotable_id=ob.annotable.id)
        if isinstance(ob, AssetVersion):
            notify.send(ob.asset)
        else:
            notify.send(ob)
        return dict(msg='deleted note "%s"' % note.id, result='success')
    
    # Custom REST-like actions
    custom_actions = ['pin', 'unpin']

    @project_set_active
    @require(is_project_admin())
    @expose('json')
    @expose('spam.templates.forms.result')
    @validate(f_confirm)
    def pin(self, proj, note_id):
        """Pin a note."""
        session = session_get()
        note = note_get(note_id)
        ob = note.annotated
        
        note.sticky = True
        session.refresh(ob.annotable)
        
        notify.send(note, update_type='updated', annotable_id=ob.annotable.id)
        notify.send(ob)
        return dict(msg='pinned note "%s"' % note.id, result='success')
    
    @project_set_active
    @require(is_project_admin())
    @expose('json')
    @expose('spam.templates.forms.result')
    @validate(f_confirm)
    def unpin(self, proj, note_id):
        """Un-pin a note."""
        session = session_get()
        note = note_get(note_id)
        ob = note.annotated
        
        note.sticky = False
        session.refresh(ob.annotable)
        
        notify.send(note, update_type='updated', annotable_id=ob.annotable.id)
        notify.send(ob)
        return dict(msg='un-pinned note "%s"' % note.id, result='success')
    

