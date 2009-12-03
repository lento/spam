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
                ('Tasks', 'tab/tasks'),
               ]
        return dict(page='%s' % libgroup.name, tabs=tabs, 
                                    sidebar=('projects', libgroup.project.id))

    @project_set_active
    @require(is_project_admin())
    @expose('spam.templates.forms.form')
    def new(self, proj, parent_id=None, **kwargs):
        """Display a NEW form."""
        tmpl_context.form = f_new
        project = tmpl_context.project
        if parent_id:
            parent = libgroup_get(project.id, parent_id)

        fargs = dict(proj=project.id, project_=project.name,
                     parent_id=parent_id)
        fcargs = dict()
        return dict(title='Create a new libgroup', args=fargs,
                                                            child_args=fcargs)

    @project_set_active
    @require(is_project_admin())
    @expose('json')
    @expose('spam.templates.forms.result')
    @validate(f_new, error_handler=new)
    def post(self, proj, parent_id, name, description=None, **kwargs):
        """Create a new scene"""
        session = session_get()
        project = tmpl_context.project
        parent = parent_id and libgroup_get(proj, parent_id) or None
        
        # add libgroup to db
        libgroup = LibraryGroup(project.id, name, parent, description)
        session.add(libgroup)
        session.flush()
        
        # create directories
        #repo.libgroup_create_dirs(project.id, libgroup.id)
        
        # send a stomp message to notify clients
        notify.send(libgroup, update_type='added')
        return dict(msg='created libgroup "%s"' % libgroup.name,
                                                            result='success')
    
    '''
    @project_set_active
    @require(is_project_admin())
    @expose('spam.templates.forms.form')
    def edit(self, proj, sc, **kwargs):
        """Display a EDIT form."""
        tmpl_context.form = f_edit
        scene = scene_get(proj, sc)

        fargs = dict(proj=scene.project.id, project_=scene.project.name,
                     sc=scene.name, name_=scene.name,
                     description=scene.description)
        fcargs = dict()
        return dict(title='Edit scene "%s"' % scene.path,
                                                args=fargs, child_args=fcargs)
        
    @project_set_active
    @require(is_project_admin())
    @expose('json')
    @expose('spam.templates.forms.result')
    @validate(f_edit, error_handler=edit)
    def put(self, proj, sc, description=None, **kwargs):
        """Edit a scene"""
        scene = scene_get(proj, sc)

        if description: scene.description = description
        notify.send(scene)
        return dict(msg='updated scene "%s"' % scene.path, result='success')

    @project_set_active
    @require(is_project_admin())
    @expose('spam.templates.forms.form')
    def get_delete(self, proj, sc, **kwargs):
        """Display a DELETE confirmation form."""
        tmpl_context.form = f_confirm
        scene = scene_get(proj, sc)

        fargs = dict(_method='DELETE',
                     proj=scene.project.id, project_=scene.project.name,
                     sc=scene.name, name_=scene.name,
                     description_=scene.description)
        fcargs = dict()
        warning = ('This will only delete the scene entry in the database. '
                   'The data must be deleted manually if needed.')
        return dict(
                title='Are you sure you want to delete "%s"?' % scene.path,
                warning=warning, args=fargs, child_args=fcargs)

    @project_set_active
    @require(is_project_admin())
    @expose('json')
    @expose('spam.templates.forms.result')
    @validate(f_confirm, error_handler=get_delete)
    def post_delete(self, proj, sc, **kwargs):
        """Delete a scene.
        
        Only delete the scene record from the db, the scene directories must be
        removed manually.
        (This should help prevent awful accidents) ;)
        """
        session = session_get()
        scene = scene_get(proj, sc)
        
        session.delete(scene)
        notify.send(scene, update_type='deleted')
        return dict(msg='deleted scene "%s"' % scene.path, result='success')
    
    # Custom REST-like actions
    custom_actions = []
'''
