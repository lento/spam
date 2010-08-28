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
"""Libgroup main controller"""

from tg import expose, url, tmpl_context, validate, require
from tg.controllers import RestController
from tg.decorators import with_trailing_slash
from pylons.i18n import ugettext as _, lazy_ugettext as l_
from spam.model import session_get, Project, User, Libgroup, libgroup_get
from spam.model import diff_dicts
from spam.lib.widgets import FormLibgroupNew, FormLibgroupEdit
from spam.lib.widgets import FormLibgroupConfirm, TableLibgroups
from spam.lib import repo
from spam.lib.notifications import notify, TOPIC_LIBGROUPS
from spam.lib.notifications import TOPIC_PROJECT_STRUCTURE
from spam.lib.journaling import journal
from spam.lib.decorators import project_set_active
from spam.lib.predicates import is_project_user, is_project_admin

from tabs import TabController

import logging
log = logging.getLogger(__name__)

# form widgets
f_new = FormLibgroupNew(action=url('/libgroup'))
f_edit = FormLibgroupEdit(action=url('/libgroup'))
f_confirm = FormLibgroupConfirm(action=url('/libgroup'))

# livetable widgets
t_libgroups = TableLibgroups()

class Controller(RestController):
    """REST controller for managing library groups.
    
    In addition to the standard REST verbs this controller defines the following
    REST-like methods:
        * ``subgroups``  (:meth:`get_subgroups`)
    """
        
    tab = TabController()
    
    @project_set_active
    @require(is_project_user())
    @expose('spam.templates.libgroup.get_all')
    def get_all(self, proj):
        """Return a `tab` page with a list of libgroups for a project and a
        button to add new libgroups.
        
        This page is used as the `library` tab in the project view:
        :meth:`spam.controllers.project.main.get_one`.
        """
        project = tmpl_context.project
        user = tmpl_context.user
        tmpl_context.t_libgroups = t_libgroups
        extra_data = dict(project=project, user_id=user.user_id)
        return dict(page='libgroups', sidebar=('projects', project.id),
            libgroups=project.libgroups, parent_id=None, extra_data=extra_data)

    @expose('spam.templates.libgroup.get_all')
    def _default(self, proj, *args, **kwargs):
        """Catch request to `libgroup/<something>' and pass them to :meth:`get_all`,
        because RESTController doesn't dispatch to get_all when there are
        arguments.
        """
        return self.get_all(proj)

    @project_set_active
    @require(is_project_user())
    @with_trailing_slash
    @expose('json')
    @expose('spam.templates.tabbed_content')
    def get_one(self, proj, libgroup_id):
        """Return a `tabbed` page for libgroup tabs."""
        libgroup = libgroup_get(proj, libgroup_id)
        
        tabs = [('Summary', 'tab/summary'),
                ('Subgroups', url('/libgroup/%s/%s/subgroups' %
                                        (libgroup.project.id, libgroup.id))),
                ('Assets', url('/asset/%s/libgroup/%s' %
                                        (libgroup.project.id, libgroup.id))),
               ]
        return dict(page='%s' % libgroup.path, libgroup=libgroup, tabs=tabs, 
                                    sidebar=('projects', libgroup.project.id))

    @project_set_active
    @require(is_project_admin())
    @expose('spam.templates.forms.form')
    def new(self, proj, parent_id=None, **kwargs):
        """Display a NEW form."""
        project = tmpl_context.project
        parent = parent_id and libgroup_get(project.id, parent_id) or None

        f_new.value = dict(proj=project.id,
                           parent_id=parent_id,
                           project_name_=project.name,
                           parent_=parent and parent.name or '',
                          )
        tmpl_context.form = f_new
        return dict(title=_('Create a new libgroup'))

    @project_set_active
    @require(is_project_admin())
    @expose('json')
    @expose('spam.templates.forms.result')
    @validate(f_new, error_handler=new)
    def post(self, proj, parent_id, name, description=None):
        """Create a new libgroup"""
        session = session_get()
        project = tmpl_context.project
        user = tmpl_context.user
        parent = parent_id and libgroup_get(proj, parent_id) or None
        
        # add libgroup to db
        libgroup = Libgroup(project.id, name, parent, description)
        session.add(libgroup)
        session.flush()
        
        # create directories
        repo.libgroup_create_dirs(project.id, libgroup)
        
        # invalidate project cache
        project.touch()

        msg = '%s %s' % (_('Created libgroup'), libgroup.path)

        # log into Journal
        journal.add(user, '%s - %s' % (msg, libgroup))
        
        # notify clients
        updates = [
            dict(item=libgroup, type='added', topic=TOPIC_LIBGROUPS),
            dict(item=project, type='updated', topic=TOPIC_PROJECT_STRUCTURE),
            ]
        notify.send(updates)

        return dict(msg=msg, status='ok', updates=updates)
    
    @project_set_active
    @require(is_project_admin())
    @expose('spam.templates.forms.form')
    def edit(self, proj, libgroup_id, **kwargs):
        """Display a EDIT form."""
        libgroup = libgroup_get(proj, libgroup_id)

        f_edit.value = dict(proj=libgroup.project.id,
                            libgroup_id=libgroup.id,
                            project_name_=libgroup.project.name,
                            libgroup_name_=libgroup.name,
                            description=libgroup.description,
                           )
        tmpl_context.form = f_edit
        return dict(title='%s %s' % (_('Edit libgroup:'), libgroup.path))
        
    @project_set_active
    @require(is_project_admin())
    @expose('json')
    @expose('spam.templates.forms.result')
    @validate(f_edit, error_handler=edit)
    def put(self, proj, libgroup_id, description=None):
        """Edit a libgroup"""
        session = session_get()
        user = tmpl_context.user
        libgroup = libgroup_get(proj, libgroup_id)
        old = libgroup.__dict__.copy()

        modified = False
        if description is not None and not libgroup.description == description:
            libgroup.description = description
            modified = True
        
        if modified:
            new = libgroup.__dict__.copy()

            msg = '%s %s' % (_('Updated libgroup:'), libgroup.path)

            # log into Journal
            journal.add(user, '%s - %s' % (msg, diff_dicts(old, new)))
            
            # notify clients
            updates = [
                dict(item=libgroup, type='updated', topic=TOPIC_LIBGROUPS),
                ]
            notify.send(updates)

            return dict(msg=msg, status='ok', updates=updates)
        return dict(msg='%s %s' % (_('Libgroup is unchanged:'), libgroup.path),
                                                    status='info', updates=[])

    @project_set_active
    @require(is_project_admin())
    @expose('spam.templates.forms.form')
    def get_delete(self, proj, libgroup_id, **kwargs):
        """Display a DELETE confirmation form."""
        libgroup = libgroup_get(proj, libgroup_id)
        f_confirm.custom_method = 'DELETE'
        f_confirm.value = dict(proj=libgroup.project.id,
                              libgroup_id=libgroup.id,
                              project_name_=libgroup.project.name,
                              libgroup_name_=libgroup.name,
                              description_=libgroup.description,
                             )
        warning = ('This will only delete the libgroup entry in the database. '
                   'The data must be deleted manually if needed.')
        tmpl_context.form = f_confirm
        return dict(title='%s %s?' % (_('Are you sure you want to delete:'),
                                                libgroup.path), warning=warning)

    @project_set_active
    @require(is_project_admin())
    @expose('json')
    @expose('spam.templates.forms.result')
    @validate(f_confirm, error_handler=get_delete)
    def post_delete(self, proj, libgroup_id):
        """Delete a libgroup.
        
        Only delete the libgroup record from the db, the scene directories must
        be removed manually.
        (This should help prevent awful accidents) ;)
        """
        project = tmpl_context.project
        session = session_get()
        user = tmpl_context.user
        libgroup = libgroup_get(proj, libgroup_id)
        if libgroup.subgroups:
            return dict(msg='%s %s' % (
                    _('Cannot delete libgroup because it contains subgroups'),
                    libgroup.path),
                status='error')
        if libgroup.assets:
            return dict(msg='%s %s' % (
                    _('Cannot delete libgroup because it contains assets'),
                    libgroup.path),
                status='error')

        session.delete(libgroup)

        # delete association objects or they will be orphaned
        session.flush()
        session.delete(libgroup.container)
        session.delete(libgroup.taggable)
        session.delete(libgroup.annotable)

        # invalidate project cache
        project.touch()

        msg = '%s %s' % (_('Deleted libgroup:'), libgroup.path)

        # log into Journal
        journal.add(user, '%s - %s' % (msg, libgroup))
        
        # notify clients
        updates = [
            dict(item=libgroup, type='deleted', topic=TOPIC_LIBGROUPS),
            dict(item=project, type='updated', topic=TOPIC_PROJECT_STRUCTURE),
            ]
        notify.send(updates)

        return dict(msg=msg, status='ok', updates=updates)
    

    # Custom REST-like actions
    _custom_actions = ['subgroups']

    @project_set_active
    @require(is_project_user())
    @expose('spam.templates.libgroup.get_all')
    def get_subgroups(self, proj, parent_id):
        """Return a `tab` page with a list of subgroups for a libgroup.
        
        This page is used as the `subgroups` tab in the libgroup view:
        :meth:`spam.controllers.libgroup.main.get_one`.
        """
        project = tmpl_context.project
        user = tmpl_context.user
        parent = libgroup_get(proj, parent_id)
        tmpl_context.t_libgroups = t_libgroups
        tmpl_context.parent = parent
        extra_data = dict(project=project, user_id=user.user_id)
        return dict(libgroups=parent.subgroups, parent_id=parent_id,
                                                        extra_data=extra_data)


