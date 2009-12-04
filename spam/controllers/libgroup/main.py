from tg import expose, url, tmpl_context, validate, require
from tg.controllers import RestController
from tg.decorators import with_trailing_slash
from spam.model import session_get, Project, User, LibraryGroup, libgroup_get
from spam.lib.widgets import FormLibgroupNew, FormLibgroupEdit
from spam.lib.widgets import FormLibgroupConfirm, TableLibgroups
from spam.lib import repo
from spam.lib.notifications import notify
from spam.lib.decorators import project_set_active
from spam.lib.predicates import is_project_user, is_project_admin

from tabs import TabController

import logging
log = logging.getLogger(__name__)

# form widgets
f_new = FormLibgroupNew(action=url('/libgroup/'))
f_edit = FormLibgroupEdit(action=url('/libgroup/'))
f_confirm = FormLibgroupConfirm(action=url('/libgroup/'))

# livetable widgets
t_libgroups = TableLibgroups()

class Controller(RestController):
    
    tab = TabController()
    
    @project_set_active
    @require(is_project_user())
    @expose('spam.templates.project.tabs.library')
    def get_all(self, proj):
        project = tmpl_context.project
        tmpl_context.t_libgroups = t_libgroups
        return dict(page='libgroups', sidebar=('projects', project.id),
                                                    libgroups=project.libgroups)

    @expose('spam.templates.project.tabs.library')
    def default(self, proj, *args, **kwargs):
        return self.get_all(proj)

    @project_set_active
    @require(is_project_user())
    @with_trailing_slash
    @expose('json')
    @expose('spam.templates.tabbed_content')
    def get_one(self, proj, libgroup_id):
        libgroup = libgroup_get(proj, libgroup_id)
        
        tabs = [('Summary', 'tab/summary'),
                ('Assets', url('/asset/%s/libgroup/%s' %
                                        (libgroup.project.id, libgroup.id))),
                ('Subgroups', url('/libgroup/%s/%s/subgroups' %
                                        (libgroup.project.id, libgroup.id))),
               ]
        return dict(page='%s' % libgroup.path, tabs=tabs, 
                                    sidebar=('projects', libgroup.project.id))

    @project_set_active
    @require(is_project_admin())
    @expose('spam.templates.forms.form')
    def new(self, proj, parent_id=None, **kwargs):
        """Display a NEW form."""
        tmpl_context.form = f_new
        project = tmpl_context.project
        parent = parent_id and libgroup_get(project.id, parent_id) or None

        fargs = dict(proj=project.id, project_=project.name,
                     parent_id=parent_id, parent_=parent and parent.name or '')
        fcargs = dict()
        return dict(title='Create a new libgroup', args=fargs,
                                                            child_args=fcargs)

    @project_set_active
    @require(is_project_admin())
    @expose('json')
    @expose('spam.templates.forms.result')
    @validate(f_new, error_handler=new)
    def post(self, proj, parent_id, name, description=None, **kwargs):
        """Create a new libgroup"""
        session = session_get()
        project = tmpl_context.project
        parent = parent_id and libgroup_get(proj, parent_id) or None
        
        # add libgroup to db
        libgroup = LibraryGroup(project.id, name, parent, description)
        session.add(libgroup)
        session.flush()
        
        # create directories
        repo.libgroup_create_dirs(project.id, libgroup)
        
        # invalidate project cache
        project.touch()
        
        # send a stomp message to notify clients
        notify.send(libgroup, update_type='added')
        notify.send(project)
        return dict(msg='created libgroup "%s"' % libgroup.path,
                                                            result='success')
    
    @project_set_active
    @require(is_project_admin())
    @expose('spam.templates.forms.form')
    def edit(self, proj, libgroup_id, **kwargs):
        """Display a EDIT form."""
        tmpl_context.form = f_edit
        libgroup = libgroup_get(proj, libgroup_id)

        fargs = dict(proj=libgroup.project.id, project_=libgroup.project.name,
                     libgroup_id=libgroup.id, name_=libgroup.name,
                     description=libgroup.description)
        fcargs = dict()
        return dict(title='Edit libgroup "%s"' % libgroup.path,
                                                args=fargs, child_args=fcargs)
        
    @project_set_active
    @require(is_project_admin())
    @expose('json')
    @expose('spam.templates.forms.result')
    @validate(f_edit, error_handler=edit)
    def put(self, proj, libgroup_id, description=None, **kwargs):
        """Edit a libgroup"""
        libgroup = libgroup_get(proj, libgroup_id)

        if description: libgroup.description = description
        notify.send(libgroup)
        return dict(msg='updated scene "%s"' % libgroup.path, result='success')

    @project_set_active
    @require(is_project_admin())
    @expose('spam.templates.forms.form')
    def get_delete(self, proj, libgroup_id, **kwargs):
        """Display a DELETE confirmation form."""
        tmpl_context.form = f_confirm
        libgroup = libgroup_get(proj, libgroup_id)

        fargs = dict(_method='DELETE',
                     proj=libgroup.project.id, project_=libgroup.project.name,
                     libgroup_id=libgroup.id, name_=libgroup.name,
                     description_=libgroup.description)
        fcargs = dict()
        warning = ('This will only delete the libgroup entry in the database. '
                   'The data must be deleted manually if needed.')
        return dict(
                title='Are you sure you want to delete "%s"?' % libgroup.path,
                warning=warning, args=fargs, child_args=fcargs)

    @project_set_active
    @require(is_project_admin())
    @expose('json')
    @expose('spam.templates.forms.result')
    @validate(f_confirm, error_handler=get_delete)
    def post_delete(self, proj, libgroup_id, **kwargs):
        """Delete a libgroup.
        
        Only delete the libgroup record from the db, the scene directories must
        be removed manually.
        (This should help prevent awful accidents) ;)
        """
        project = tmpl_context.project
        session = session_get()
        libgroup = libgroup_get(proj, libgroup_id)
        if libgroup.subgroups:
            return dict(msg='cannot delete libgroup "%s" because it contains '
                            'subgroups' % libgroup.path,
                        result='failed')
        if libgroup.assets:
            return dict(msg='cannot delete libgroup "%s" because it contains '
                            'assets' % libgroup.path,
                        result='failed')
        
        session.delete(libgroup)

        # invalidate project cache
        project.touch()
        
        notify.send(libgroup, update_type='deleted')
        notify.send(project)
        return dict(msg='deleted libgroup "%s"' % libgroup_id,
                                                            result='success')
    

    # Custom REST-like actions
    custom_actions = ['subgroups']

    @project_set_active
    @require(is_project_user())
    @expose('spam.templates.project.tabs.library')
    def get_subgroups(self, proj, parent_id):
        tmpl_context.t_libgroups = t_libgroups
        project = tmpl_context.project
        parent = libgroup_get(proj, parent_id)
        tmpl_context.parent = parent
        return dict(libgroups=parent.subgroups)


