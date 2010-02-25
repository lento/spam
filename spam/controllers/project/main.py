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
"""Project main controller"""

from tg import expose, url, tmpl_context, redirect, validate, require
from tg.controllers import RestController
from tg.decorators import with_trailing_slash
from pylons.i18n import ugettext as _, lazy_ugettext as l_
from spam.model import session_get, project_get, Project, User
from spam.model import query_projects, query_projects_archived, diff_dicts
from spam.lib.widgets import FormProjectNew, FormProjectEdit, FormProjectConfirm
from spam.lib.widgets import ProjectsActive, ProjectsArchived
from spam.lib import repo
from spam.lib.notifications import notify
from spam.lib.journaling import journal
from spam.lib.decorators import project_set_active
from spam.lib.predicates import is_project_user, is_project_admin
from repoze.what.predicates import in_group

from tabs import TabController

import logging
log = logging.getLogger(__name__)

# form widgets
f_new = FormProjectNew(action=url('/project/'))
f_edit = FormProjectEdit(action=url('/project/'))
f_confirm = FormProjectConfirm(action=url('/project/'))

# livetable widgets
w_projects_active = ProjectsActive()
w_projects_archived = ProjectsArchived()

class Controller(RestController):
    """REST controller for managing projects.
    
    In addition to the standard REST verbs this controller defines the following
    REST-like methods:
        * ``archive``  (:meth:`get_archive`, :meth:`post_archive`)
        * ``activate`` (:meth:`get_activate`, :meth:`post_activate`)
        * ``upgrade``  (:meth:`get_upgrade`, :meth:`post_upgrade`)
        * ``sidebar``  (:meth:`get_sidebar`)
    """
    
    tab = TabController()
    
    @require(in_group('administrators'))
    @expose('spam.templates.project.get_all')
    def get_all(self):
        """Return a `full` page for managing active and archived projects.
        
        This page is linked from the `admin` sidebar.
        """
        tmpl_context.projects_active = w_projects_active
        tmpl_context.projects_archived = w_projects_archived
        active = query_projects()
        archived = query_projects_archived()
        return dict(page='admin/project', sidebar=('admin', 'projects'),
                                            active=active, archived=archived)

    @project_set_active
    @require(is_project_user())
    @with_trailing_slash
    @expose('json')
    @expose('spam.templates.tabbed_content')
    def get_one(self, proj):
        """Return a `tabbed` page for project tabs."""
        project = tmpl_context.project
        tabs = [('Summary', 'tab/summary'),
                ('Scenes', url('/scene/%s' % project.id)),
                ('Library', url('/libgroup/%s' % project.id)),
               ]
        if is_project_admin():
            tabs.append(('Users', 'tab/users'))
        
        return dict(page='project/%s' % project.id, project=project, tabs=tabs,
                                            sidebar=('projects', project.id))


    @require(in_group('administrators'))
    @expose('spam.templates.forms.form')
    def new(self, **kwargs):
        """Display a NEW form."""
        tmpl_context.form = f_new
        fargs = dict()
        fcargs = dict()
        return dict(title='Create a new project', args=fargs, child_args=fcargs)

    @require(in_group('administrators'))
    @expose('json')
    @expose('spam.templates.forms.result')
    @validate(f_new, error_handler=new)
    def post(self, proj, name=None, description=None):
        """Create a new project"""
        session = session_get()
        user = tmpl_context.user
        
        # add project to db
        project = Project(proj, name=name, description=description)
        session.add(project)
        
        # create directories and init hg repo
        repo.project_create_dirs(project.id)
        repo.repo_init(project.id)
        
        # grant project rights to user "admin"
        admin = session.query(User).filter_by(user_name=u'admin').one()
        project.admins.append(admin)
        
        # log into Journal
        journal.add(user, 'created %s' % project)
        
        # send a stomp message to notify clients
        notify.send(project, update_type='added')
        return dict(msg='created project "%s"' % project.id, result='success',
                                                                project=project)
    
    @project_set_active
    @require(in_group('administrators'))
    @expose('spam.templates.forms.form')
    def edit(self, proj, **kwargs):
        """Display a EDIT form."""
        tmpl_context.form = f_edit
        project = tmpl_context.project
        fargs = dict(proj=project.id, id_=project.id, name=project.name,
                                                description=project.description)
        fcargs = dict()
        return dict(title='Edit project "%s"' % proj, args=fargs,
                                                            child_args=fcargs)
        
    @project_set_active
    @require(in_group('administrators'))
    @expose('json')
    @expose('spam.templates.forms.result')
    @validate(f_edit, error_handler=edit)
    def put(self, proj, name=None, description=None):
        """Edit a project"""
        project = tmpl_context.project
        old = project.__dict__.copy()
        session = session_get()
        user = tmpl_context.user
        
        modified = False
        if name:
            project.name = name
            modified = True
            
        if description:
            project.description = description
            modified = True
        
        if modified:
            new = project.__dict__.copy()
        
            # invalidate cache
            project.touch()

            # log into Journal
            journal.add(user, u'modified %s: %s' %
                                            (project, diff_dicts(old, new)))
        
            # send a stomp message to notify clients
            notify.send(project, update_type='updated')
            return dict(msg='updated project "%s"' % proj, result='success')
        return dict(msg='project "%s" unchanged' % proj, result='success')

    @project_set_active
    @require(in_group('administrators'))
    @expose('spam.templates.forms.form')
    def get_delete(self, proj, **kwargs):
        """Display a DELETE confirmation form."""
        tmpl_context.form = f_confirm
        project = tmpl_context.project
        fargs = dict(_method='DELETE', proj=project.id, id_=project.id,
                     name_=project.name,
                     description_=project.description,
                    )
        fcargs = dict()
        warning = ('This will only delete the project entry in the database. '
                   'The data and history of the project must be deleted '
                   'manually if needed.')
        return dict(
                title='Are you sure you want to delete "%s"?' % project.name,
                warning=warning, args=fargs, child_args=fcargs)

    @project_set_active
    @require(in_group('administrators'))
    @expose('json')
    @expose('spam.templates.forms.result')
    @validate(f_confirm, error_handler=get_delete)
    def post_delete(self, proj):
        """Delete a project.
        
        Only delete the project record from the common db, the project
        repository must be removed manually.
        (This should help prevent awful accidents) ;)
        """
        session = session_get()
        user = tmpl_context.user
        project = tmpl_context.project
        
        session.delete(project)
        
        # log into Journal
        journal.add(user, 'deleted %s' % project)
        
        # send a stomp message to notify clients
        notify.send(project, update_type='deleted')
        return dict(msg='deleted project "%s"' % proj, result='success')
    
    # Custom REST-like actions
    _custom_actions = ['archive', 'activate', 'upgrade', 'sidebar']
    
    @project_set_active
    @require(in_group('administrators'))
    @expose('spam.templates.forms.form')
    def get_archive(self, proj, **kwargs):
        """Display a ARCHIVE confirmation form."""
        tmpl_context.form = f_confirm
        project = tmpl_context.project
        fargs = dict(_method='ARCHIVE', proj=project.id, id_=project.id,
                     name_=project.name,
                     description_=project.description,
                    )
        fcargs = dict()
        return dict(title='Are you sure you want to archive "%s"' % proj,
                                                args=fargs, child_args=fcargs)

    @project_set_active
    @require(in_group('administrators'))
    @expose('json')
    @expose('spam.templates.forms.result')
    def post_archive(self, proj):
        """Archive a project"""
        project = tmpl_context.project
        session = session_get()
        user = tmpl_context.user

        project.archived = True

        # invalidate cache
        project.touch()

        # log into Journal
        journal.add(user, 'archived %s' % project)
        
        # send a stomp message to notify clients
        notify.send(project, update_type='archived')
        return dict(msg='archived project "%s"' % proj, result='success')

    @require(in_group('administrators'))
    @expose('spam.templates.forms.form')
    def get_activate(self, proj, **kwargs):
        """Display a ACTIVATE confirmation form."""
        tmpl_context.form = f_confirm
        query = query_projects_archived().filter_by(id=proj.decode('utf-8'))
        project = query.one()
        
        fargs = dict(_method='ACTIVATE', proj=project.id, id_=project.id,
                     name_=project.name,
                     description_=project.description,
                    )
        fcargs = dict()
        return dict(title='Are you sure you want to activate "%s"' % proj,
                                                args=fargs, child_args=fcargs)

    @require(in_group('administrators'))
    @expose('json')
    @expose('spam.templates.forms.result')
    def post_activate(self, proj):
        """Activate a project"""
        query = query_projects_archived().filter_by(id=proj.decode('utf-8'))
        project = query.one()
        session = session_get()
        user = tmpl_context.user

        project.archived = False

        # invalidate cache
        project.touch()

        # log into Journal
        journal.add(user, 'activated %s' % project)
        
        # send a stomp message to notify clients
        notify.send(project, update_type='activated')
        return dict(msg='activated project "%s"' % proj, result='success')

    @project_set_active
    @require(in_group('administrators'))
    @expose('spam.templates.forms.form')
    def get_upgrade(self, proj, **kwargs):
        """Display a UPGRADE confirmation form."""
        tmpl_context.form = f_confirm
        project = tmpl_context.project
        
        fargs = dict(_method='UPGRADE', proj=project.id, id_=project.id,
                     name_=project.name,
                     description_=project.description,
                    )
        fcargs = dict()
        return dict(title='Are you sure you want to upgrade "%s" schema?' %
                                            proj, args=fargs, child_args=fcargs)

    @project_set_active
    @require(in_group('administrators'))
    @expose('json')
    @expose('spam.templates.forms.result')
    def post_upgrade(self, proj):
        """Upgrade the DB schema for a project"""
        project = tmpl_context.project
        project.schema_upgrade()
        project.touch()
        notify.send(project, update_type='updated')
        return dict(msg='upgraded project "%s" schema' % proj, result='success')

    @project_set_active
    @require(is_project_user())
    @expose('spam.templates.project.sidebar')
    def get_sidebar(self, proj):
        """Return a html fragment containing the `project` sidebar. This is used
        to dynamically reload the sidebar when the project structure changes
        without reloading the whole page."""
        project = tmpl_context.project
        return dict()
