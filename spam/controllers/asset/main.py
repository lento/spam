from tg import expose, url, tmpl_context, validate, require
from tg.controllers import RestController
from tg.decorators import with_trailing_slash
from spam.model import session_get, Asset, AssetCategory, category_get
from spam.model import project_get_eager, project_get, container_get, asset_get
from spam.lib.widgets import FormAssetNew, FormAssetEdit, FormAssetConfirm
from spam.lib.widgets import TableAssets, TableAssetHistory, NotifyClientJS
from spam.lib import repo
from spam.lib.notifications import notify
from spam.lib.decorators import project_set_active
from spam.lib.predicates import is_project_user, is_project_admin

import logging
log = logging.getLogger(__name__)

# form widgets
f_new = FormAssetNew(action=url('/asset/'))
f_edit = FormAssetEdit(action=url('/asset/'))
f_confirm = FormAssetConfirm(action=url('/asset/'))

# livetable widgets
t_assets = TableAssets()
t_history = TableAssetHistory()

# javascripts
j_notify_client = NotifyClientJS()

class Controller(RestController):
    
    @project_set_active
    @require(is_project_user())
    @expose('spam.templates.asset.get_all')
    def get_all(self, proj, container_type, container_id):
        project = tmpl_context.project
        tmpl_context.t_assets = t_assets
        tmpl_context.j_notify_client = j_notify_client
        container = container_get(proj, container_type, container_id)
        
        assets_per_category = {}
        for a in container.assets:
            cat = a.category.name
            if cat not in assets_per_category:
                assets_per_category[cat] = []
            assets_per_category[cat].append(a)
        
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

        query = session_get().query(AssetCategory)
        categories = query.order_by('ordering', 'name')
        category_choices = [(0, '')]
        category_choices.extend([(cat.id, cat.name) for cat in categories])
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
        asset = Asset(project.id, container, category, name, user)
        session.add(asset)
        session.flush()
        
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
                     category_=asset.category.name,
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
        asset = asset_get(proj, asset_id)
        
        session.delete(asset)
        notify.send(asset, update_type='deleted')
        return dict(msg='deleted asset "%s"' % asset.path, result='success')
    
    # Custom REST-like actions
    custom_actions = ['checkout', 'release']

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
        
        The asset will be unblocked and available to project users to checkout.
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


