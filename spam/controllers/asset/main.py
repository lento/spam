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
"""Asset controller"""

from tg import expose, url, tmpl_context, validate, require
from tg.controllers import RestController
from tg.decorators import with_trailing_slash
from tw.forms import validators
from spam.model import session_get, Asset, AssetVersion, Category, category_get
from spam.model import project_get, container_get, asset_get, Journal
from spam.lib.widgets import FormAssetNew, FormAssetEdit, FormAssetConfirm
from spam.lib.widgets import FormAssetPublish
from spam.lib.widgets import TableAssets, TableAssetHistory, NotifyClientJS
from spam.lib import repo, preview
from spam.lib.notifications import notify
from spam.lib.decorators import project_set_active
from spam.lib.predicates import is_project_user, is_project_admin

import logging
log = logging.getLogger(__name__)

# form widgets
f_new = FormAssetNew(action=url('/asset/'))
f_edit = FormAssetEdit(action=url('/asset/'))
f_confirm = FormAssetConfirm(action=url('/asset/'))
f_publish = FormAssetPublish(action=url('/asset/'))

# livetable widgets
t_assets = TableAssets()
t_history = TableAssetHistory()

# javascripts
j_notify_client = NotifyClientJS()

class Controller(RestController):
    """REST controller for managing assets"""
    
    @project_set_active
    @require(is_project_user())
    @expose('spam.templates.asset.get_all')
    def get_all(self, proj, container_type, container_id):
        """Return a `tab` page  with a list of all categories and a button to
        add new assets.
        
        This page is used as the `assets` tab in the shot and libgroup view:
            * :meth:`spam.controllers.shot.main.get_one`
            * :meth:`spam.controllers.libgroup.main.get_one`.
        """
        project = tmpl_context.project
        tmpl_context.t_assets = t_assets
        tmpl_context.j_notify_client = j_notify_client
        container = container_get(proj, container_type, container_id)
        query = session_get().query(Category)
        categories = query.order_by('ordering', 'id')
        
        assets_dict = {}
        for a in container.assets:
            cat = a.category.id
            if cat not in assets_dict:
                assets_dict[cat] = []
            assets_dict[cat].append(a)
        
        assets_per_category = []
        for cat in categories:
            if cat.id in assets_dict:
                assets_per_category.append((cat.id, assets_dict[cat.id]))
        
        return dict(page='assets', sidebar=('projects', project.id),
                container_type=container_type, container_id=container_id,
                container=container, assets_per_category=assets_per_category)

    @expose('spam.templates.asset.get_all')
    def default(self, proj, container_type, container_id, *args, **kwargs):
        return self.get_all(proj, container_type, container_id)

    @project_set_active
    @require(is_project_user())
    @with_trailing_slash
    @expose('json')
    @expose('spam.templates.asset.get_one')
    def get_one(self, proj, asset_id):
        """Return a `standalone` page with the asset history"""
        tmpl_context.t_history = t_history
        asset = asset_get(proj, asset_id)
        return dict(asset=asset)

    @project_set_active
    @require(is_project_admin())
    @expose('spam.templates.forms.form')
    def new(self, proj, container_type, container_id, **kwargs):
        """Display a NEW form."""
        tmpl_context.form = f_new
        project = tmpl_context.project
        container = container_get(project.id, container_type, container_id)
        
        fargs = dict(proj=project.id, project_=project.name,
                     container_type=container_type, container_id=container_id,
                    )

        query = session_get().query(Category)
        categories = query.order_by('ordering', 'id')
        category_choices = ['']
        category_choices.extend([cat.id for cat in categories])
        fcargs = dict(category_id=dict(options=category_choices))

        return dict(title='Create a new asset', args=fargs, child_args=fcargs)

    @project_set_active
    @require(is_project_admin())
    @expose('json')
    @expose('spam.templates.forms.result')
    @validate(f_new, error_handler=new)
    def post(self, proj, container_type, container_id, category_id, name,
             **kwargs):
        """Create a new asset"""
        session = session_get()
        project = tmpl_context.project
        user = tmpl_context.user
        container = container_get(project.id, container_type, container_id)
        category = category_get(category_id)
        
        # add asset to db
        asset = Asset(container, category, name, user)
        session.add(asset)
        session.flush()
        
        # log into Journal
        new = asset.__dict__.copy()
        new.pop('_sa_instance_state', None)
        session.add(Journal(user, 'created asset %s (%s): %s' %
                                                (asset.id, asset.path, new)))

        # send a stomp message to notify clients
        notify.send(asset, update_type='added')
        return dict(msg='created asset "%s"' % asset.name, result='success')
    
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

    '''
    @project_set_active
    @require(is_project_admin())
    @expose('spam.templates.forms.form')
    def get_delete(self, proj, asset_id, **kwargs):
        """Display a DELETE confirmation form."""
        tmpl_context.form = f_confirm
        asset = asset_get(proj, asset_id)

        fargs = dict(_method='DELETE',
                     proj=asset.project.id, project_=asset.project.name,
                     asset_id=asset.id, name_=asset.name,
                     container_=asset.parent.path,
                     category_=asset.category.id,
                    )
                     
        fcargs = dict()
        warning = ('This will only delete the asset entry in the database. '
                   'The data must be deleted manually if needed.')
        return dict(
                title='Are you sure you want to delete "%s"?' % asset.path,
                warning=warning, args=fargs, child_args=fcargs)

    @project_set_active
    @require(is_project_admin())
    @expose('json')
    @expose('spam.templates.forms.result')
    @validate(f_confirm, error_handler=get_delete)
    def post_delete(self, proj, asset_id, **kwargs):
        """Delete an asset.
        
        Only delete the asset record from the db, the asset file(s) must be
        removed manually.
        (This should help prevent awful accidents) ;)
        """
        session = session_get()
        user = tmpl_context.user
        asset = asset_get(proj, asset_id)
        
        session.delete(asset)

        # log into Journal
        session.add(Journal(user, 'deleted asset %s (%s)' %
                                                        (asset.id, asset.path)))
        
        # send a stomp message to notify clients
        notify.send(asset, update_type='deleted')
        return dict(msg='deleted asset "%s"' % asset.path, result='success')
    
    # Custom REST-like actions
    custom_actions = ['checkout', 'release', 'publish']

    @project_set_active
    @require(is_project_user())
    @expose('json')
    @expose('spam.templates.forms.result')
    @validate(f_confirm, error_handler=get_delete)
    def checkout(self, proj, asset_id, **kwargs):
        """Checkout an asset.
        
        The asset will be blocked and only the current owner will be able to
        publish new versions until it is released.
        """
        asset = asset_get(proj, asset_id)
        user = tmpl_context.user
        
        if not asset.checkedout:
            asset.user = user
            asset.checkedout = True
            notify.send(asset)
            return dict(msg='checkedout asset "%s"' % asset.path,
                                                            result='success')
        else:
            return dict(msg='asset "%s" is already checkedout' % asset.path,
                                                            result='failed')


    @project_set_active
    @require(is_project_user())
    @expose('json')
    @expose('spam.templates.forms.result')
    @validate(f_confirm, error_handler=get_delete)
    def release(self, proj, asset_id, **kwargs):
        """Release an asset.
        
        The asset will be unblocked and available for other users to checkout.
        """
        asset = asset_get(proj, asset_id)
        user = tmpl_context.user
        
        if asset.checkedout:
            asset.user = None
            asset.checkedout = False
            notify.send(asset)
            return dict(msg='released asset "%s"' % asset.path,
                                                            result='success')
        else:
            return dict(msg='asset "%s" is not checkedout' % asset.path,
                                                            result='failed')


    @project_set_active
    @require(is_project_admin())
    @expose('spam.templates.forms.form')
    def get_publish(self, proj, asset_id, **kwargs):
        """Display a PUBLISH form."""
        log.debug('asset/get_publish: %s %s' % (kwargs, tmpl_context.form_errors))
        tmpl_context.form = f_publish
        asset = asset_get(proj, asset_id)

        fargs = dict(_method='PUBLISH',
                     proj=asset.project.id, project_=asset.project.name,
                     asset_id=asset.id, name_=asset.name,
                     container_=asset.parent.path,
                     category_=asset.category.id,
                    )
                     
        fcargs = dict()
        return dict(title='Publish a new version for "%s"' % asset.path,
                                        args=fargs, child_args=fcargs)

    @project_set_active
    @require(is_project_admin())
    @expose('json')
    @expose('spam.templates.forms.result')
    @validate(f_publish, error_handler=get_publish)
    def post_publish(self, proj, asset_id, uploaded, comment='', **kwargs):
        """Publish a new version of an asset.
        
        This will commit to the repo the file(s) already uploaded in a temporary
        storage area, and create a thumbnail and preview if required.
        """
        uploaded = uploaded[1:] # the form send an empty string as first item
        log.debug('post_publish: %s' % uploaded)
        session = session_get()
        asset = asset_get(proj, asset_id)
        user = tmpl_context.user
        
        # commit file to repo
        text = u'[published v%03d]\n%s' % (asset.current_ver+1, comment)
        repo_id = repo.commit(proj, asset, uploaded, text, user.user_name)
        if not repo_id:
            return dict(msg='%s is already the latest version' %
                                                    uploaded, result='failed')
        
        # create a new version
        newver = AssetVersion(asset, asset.current_ver+1, user, repo_id)
        session.add(newver)
        session.refresh(asset)
        
        # create thumbnail and preview
        preview.make_thumb(asset)
        preview.make_preview(asset)
        
        # log into Journal
        session.add(Journal(user, 'published asset %s (%s): v%03d' %
                                            (asset.id, asset.path, newver.ver)))
        
        # send a stomp message to notify clients
        notify.send(asset)
        return dict(msg='published asset "%s"' % asset.path, result='success')

