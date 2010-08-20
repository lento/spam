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
"""Asset controller"""

import os, shutil, mimetypes
from tg import expose, url, tmpl_context, validate, require, response
from tg.controllers import RestController
from tg.decorators import with_trailing_slash
from pylons.i18n import ugettext as _, lazy_ugettext as l_
from tw.forms import validators
from spam.model import session_get, Asset, AssetVersion, Category, Note
from spam.model import project_get, container_get, asset_get, category_get
from spam.model import assetversion_get
from spam.lib.widgets import FormAssetNew, FormAssetEdit, FormAssetConfirm
from spam.lib.widgets import FormAssetPublish, FormAssetStatus, BoxStatus
from spam.lib.widgets import TableAssets, TableAssetHistory
from spam.lib import repo, preview
from spam.lib.notifications import notify
from spam.lib.journaling import journal
from spam.lib.decorators import project_set_active, asset_set_active
from repoze.what.predicates import Any
from spam.lib.predicates import is_project_user, is_project_admin
from spam.lib.predicates import is_asset_supervisor, is_asset_artist
from spam.lib.predicates import is_asset_owner

import logging
log = logging.getLogger(__name__)

# form widgets
f_new = FormAssetNew(action=url('/asset/'))
f_edit = FormAssetEdit(action=url('/asset/'))
f_confirm = FormAssetConfirm(action=url('/asset/'))
f_publish = FormAssetPublish(action=url('/asset/'))
f_status = FormAssetStatus(action=url('/asset/'))

# livewidgets
t_assets = TableAssets()
t_history = TableAssetHistory()
b_status = BoxStatus()


class Controller(RestController):
    """REST controller for managing assets.
    
    In addition to the standard REST verbs this controller defines the following
    REST-like methods:
        * ``checkout``  (:meth:`checkout`)
        * ``release`` (:meth:`release`)
        * ``publish``  (:meth:`get_publish`, :meth:`post_publish`)
        * ``submit``  (:meth:`get_submit`, :meth:`post_submit`)
        * ``recall``  (:meth:`get_recall`, :meth:`post_recall`)
        * ``sendback``  (:meth:`get_sendback`, :meth:`post_sendback`)
        * ``approve``  (:meth:`get_approve`, :meth:`post_approve`)
        * ``revoke``  (:meth:`get_revoke`, :meth:`post_revoke`)
        * ``download``  (:meth:`download`)
    """
    
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
        tmpl_context.b_status = b_status
        container = container_get(proj, container_type, container_id)
        
        return dict(page='assets', sidebar=('projects', project.id),
                container_type=container_type, container_id=container_id,
                container=container)

    @expose('spam.templates.asset.get_all')
    def _default(self, proj, container_type, container_id, *args, **kwargs):
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
        
        # thumb, ver, note
        history = []
        for ver in asset.versions:
            if ver.notes:
                for note in ver.notes:
                    history.append(dict(id=None, proj_id=None, thumbnail=None,
                                    ver=None, fmtver=None, header=note.header,
                                    text=note.text, lines=note.lines))
            else:
                history.append(dict(id=None, proj_id=None, thumbnail=None,
                                    ver=None, fmtver=None, header='',
                                    text='', lines=[]))
            
            history[-1]['id'] = ver.id
            history[-1]['proj_id'] = ver.asset.proj_id
            history[-1]['has_preview'] = ver.has_preview
            history[-1]['thumbnail'] = ver.thumbnail
            history[-1]['ver'] = ver.ver
            history[-1]['fmtver'] = ver.fmtver
        
        return dict(asset=asset, history=history)

    @project_set_active
    @require(is_project_admin())
    @expose('spam.templates.forms.form2')
    def new(self, proj, container_type, container_id, **kwargs):
        """Display a NEW form."""
        project = tmpl_context.project
        container = container_get(project.id, container_type, container_id)
        
        f_new.value = dict(proj=project.id,
                           container_type=container_type,
                           container_id=container_id,
                           project_name_=project.name,
                          )

        query = session_get().query(Category)
        categories = query.order_by('ordering', 'id')
        category_choices = ['']
        category_choices.extend([cat.id for cat in categories])
        f_new.child.children.category_id.options = category_choices

        tmpl_context.form = f_new
        return dict(title=_('Create a new asset'))

    @project_set_active
    @require(is_project_admin())
    @expose('json')
    @expose('spam.templates.forms.result')
    @validate(f_new, error_handler=new)
    def post(self, proj, container_type, container_id, category_id, name,
                                                                comment=None):
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
        text = '[%s v000]\n%s' % (_('created'), comment or '')
        asset.current.notes.append(Note(user, text))
        
        # log into Journal
        new = asset.__dict__.copy()
        new.pop('_sa_instance_state', None)
        journal.add(user, 'created %s' % asset)

        # send a stomp message to notify clients
        notify.send(asset, update_type='added')
        return dict(msg='created asset "%s"' % asset.name, result='success',
                                                                    asset=asset)
    
    @project_set_active
    @require(is_project_admin())
    @expose('spam.templates.forms.form2')
    def get_delete(self, proj, asset_id, **kwargs):
        """Display a DELETE confirmation form."""
        asset = asset_get(proj, asset_id)

        f_confirm.custom_method = 'DELETE'
        f_confirm.value = dict(proj=asset.project.id,
                               project_name_=asset.project.name,
                               container_=asset.parent.owner.path,
                               category_id_=asset.category.id,
                               asset_id=asset.id,
                               asset_name_=asset.name,
                              )
                     
        warning = ('This will only delete the asset entry in the database. '
                   'The data must be deleted manually if needed.')
        tmpl_context.form = f_confirm
        return dict(title='%s %s?' % (_('Are you sure you want to delete'),
                                                asset.path), warning=warning)

    @project_set_active
    @require(is_project_admin())
    @expose('json')
    @expose('spam.templates.forms.result')
    @validate(f_confirm, error_handler=get_delete)
    def post_delete(self, proj, asset_id):
        """Delete an asset.
        
        Only delete the asset record from the db, the asset file(s) must be
        removed manually.
        (This should help prevent awful accidents) ;)
        """
        session = session_get()
        user = tmpl_context.user
        asset = asset_get(proj, asset_id)

        session.delete(asset)

        # delete association objects or they will be orphaned
        session.flush()
        for ver in asset.versions:
            session.delete(ver.annotable)
        session.delete(asset.taggable)

        # log into Journal
        journal.add(user, 'deleted %s' % asset)
        
        # send a stomp message to notify clients
        notify.send(asset, update_type='deleted')
        return dict(msg='deleted asset "%s"' % asset.path, result='success')
    
    # Custom REST-like actions
    _custom_actions = ['checkout', 'release', 'publish', 'submit', 'recall',
                      'sendback', 'approve', 'revoke', 'download']

    @project_set_active
    @asset_set_active
    @require(Any(is_asset_supervisor(), is_asset_artist()))
    @expose('json')
    @expose('spam.templates.forms.result')
    @validate(f_confirm)
    def checkout(self, proj, asset_id):
        """Checkout an asset.
        
        The asset will be blocked and only the current owner will be able to
        publish new versions until it is released.
        """
        session = session_get()
        asset = asset_get(proj, asset_id)
        user = tmpl_context.user
        
        if not asset.checkedout:
            asset.checkout(user)
            notify.send(asset)
            notify.ancestors(asset)
            return dict(msg='checkedout asset "%s"' % asset.path,
                                                            result='success')
        else:
            return dict(msg='asset "%s" is already checkedout' % asset.path,
                                                            result='failed')


    @project_set_active
    @asset_set_active
    @require(Any(is_asset_owner(), is_asset_supervisor()))
    @expose('json')
    @expose('spam.templates.forms.result')
    @validate(f_confirm)
    def release(self, proj, asset_id):
        """Release an asset.
        
        The asset will be unblocked and available for other users to checkout.
        """
        asset = asset_get(proj, asset_id)
        user = tmpl_context.user
        
        if asset.checkedout:
            asset.release()
            notify.send(asset)
            notify.ancestors(asset)
            return dict(msg='released asset "%s"' % asset.path,
                                                            result='success')
        else:
            return dict(msg='asset "%s" is not checkedout' % asset.path,
                                                            result='failed')


    @project_set_active
    @asset_set_active
    @require(is_asset_owner())
    @expose('spam.templates.forms.form2')
    def get_publish(self, proj, asset_id, **kwargs):
        """Display a PUBLISH form."""
        asset = asset_get(proj, asset_id)

        f_publish.custom_method = 'PUBLISH'
        f_publish.value = dict(proj=asset.project.id,
                               asset_id=asset.id,
                               project_name_=asset.project.name,
                               container_=asset.parent.owner.path,
                               category_id_=asset.category.id,
                               asset_name_=asset.name,
                              )
        
        name, ext = os.path.splitext(asset.name)
        f_publish.child.children.uploader.ext = ext
        tmpl_context.form = f_publish
        return dict(title='%s %s' % (_('Publish a new version for'),
                                                                    asset.path))

    @project_set_active
    @asset_set_active
    @require(is_asset_owner())
    @expose('json')
    @expose('spam.templates.forms.result')
    @validate(f_publish, error_handler=get_publish)
    def post_publish(self, proj, asset_id, uploaded, comment=None,
                                                                uploader=None):
        """Publish a new version of an asset.
        
        This will commit to the repo the file(s) already uploaded in a temporary
        storage area, and create a thumbnail and preview if required.
        """
        session = session_get()
        asset = asset_get(proj, asset_id)
        user = tmpl_context.user

        if not asset.checkedout or user != asset.owner:
            return dict(msg='cannot publish asset "%s"' % asset_id,
                                                            result='failed')
        
        if isinstance(uploaded, list):
            # the form might send empty strings, so we strip them
            uploaded = [uf for uf in uploaded if uf]
        else:
            uploaded = [uploaded]
        
        # check that uploaded file extension matches asset name
        name, ext = os.path.splitext(asset.name)
        for uf in uploaded:
            uf_name, uf_ext = os.path.splitext(uf)
            if not uf_ext == ext:
                return dict(msg='uploaded file is not a "%s" file' % ext,
                                                                result='failed')
        
        # commit file to repo
        if comment is None or comment=='None':
            comment = ''
        header = u'[published %s v%03d]' % (asset.path, asset.current.ver+1)
        text = comment and u'%s\n%s' % (header, comment) or header
        repo_id = repo.commit(proj, asset, uploaded, text, user.user_name)
        if not repo_id:
            return dict(msg='%s is already the latest version' %
                                                    uploaded, result='failed')
        
        # create a new version
        newver = AssetVersion(asset, asset.current.ver+1, user, repo_id)
        text = u'[published v%03d]\n%s' % (asset.current.ver+1, comment)
        newver.notes.append(Note(user, text))
        session.add(newver)
        session.refresh(asset)
        
        # create thumbnail and preview
        preview.make_thumb(asset)
        preview.make_preview(asset)
        
        # log into Journal
        journal.add(user, 'published %s: v%03d' % (asset, newver.ver))
        
        # send a stomp message to notify clients
        notify.send(asset)
        return dict(msg='published asset "%s"' % asset.path, result='success',
                                                                version=newver)

    @project_set_active
    @asset_set_active
    @require(is_asset_owner())
    @expose('spam.templates.forms.form2')
    def get_submit(self, proj, asset_id, **kwargs):
        """Display a SUBMIT form."""
        asset = asset_get(proj, asset_id)

        f_status.custom_method = 'SUBMIT'
        f_status.value = dict(proj=asset.project.id,
                              asset_id=asset.id,
                              project_name_=asset.project.name,
                              container_=asset.parent.owner.path,
                              category_id_=asset.category.id,
                              asset_name_=asset.name,
                             )
                     
        tmpl_context.form = f_status
        return dict(title='%s: %s' % (_('Submit for approval'), asset.path))

    @project_set_active
    @asset_set_active
    @require(is_asset_owner())
    @expose('json')
    @expose('spam.templates.forms.result')
    @validate(f_status, error_handler=get_submit)
    def post_submit(self, proj, asset_id, comment=None):
        """Submit an asset to supervisors for approval."""
        session = session_get()
        user = tmpl_context.user
        asset = asset_get(proj, asset_id)
        
        if not asset.submitted and not asset.approved:
            asset.submit(user)
            text = u'[%s v%03d]\n%s' % (_('submitted'), asset.current.ver,
                                                                comment or '')
            asset.current.notes.append(Note(user, text))
            session.refresh(asset.current.annotable)
            
            # log into Journal
            journal.add(user, 'submitted %s' % asset)
            
            # send a stomp message to notify clients
            notify.send(asset)
            notify.ancestors(asset)
            return dict(msg='submitted asset "%s"' % asset.path,
                                                            result='success')
        return dict(msg='asset "%s" cannot be submitted' % asset.path,
                                                            result='failed')
    
    @project_set_active
    @asset_set_active
    @require(is_asset_owner())
    @expose('spam.templates.forms.form2')
    def get_recall(self, proj, asset_id, **kwargs):
        """Display a RECALL form."""
        asset = asset_get(proj, asset_id)

        f_status.custom_method = 'RECALL'
        f_status.value = dict(proj=asset.project.id,
                              asset_id=asset.id,
                              project_name_=asset.project.name,
                              container_=asset.parent.owner.path,
                              category_id_=asset.category.id,
                              asset_name_=asset.name,
                             )
                     
        tmpl_context.form = f_status
        return dict(title='%s: %s' % (_('Recall submission for'), asset.path))

    @project_set_active
    @asset_set_active
    @require(is_asset_owner())
    @expose('json')
    @expose('spam.templates.forms.result')
    @validate(f_status, error_handler=get_submit)
    def post_recall(self, proj, asset_id, comment=None):
        """Recall an asset submitted for approval."""
        session = session_get()
        user = tmpl_context.user
        asset = asset_get(proj, asset_id)
        
        if asset.submitted and not asset.approved:
            asset.recall(user)
            text = u'[%s v%03d]\n%s' % (_('recalled'), asset.current.ver,
                                                                comment or '')
            asset.current.notes.append(Note(user, text))
            session.refresh(asset.current.annotable)

            # log into Journal
            journal.add(user, 'recall submission for %s' % asset)
        
            # send a stomp message to notify clients
            notify.send(asset)
            notify.ancestors(asset)
            return dict(msg='recalled submission for asset "%s"' % asset.path,
                                                            result='success')
        return dict(msg='submission for asset "%s" cannot be recalled' %
                                                    asset.path, result='failed')

    @project_set_active
    @asset_set_active
    @require(is_asset_supervisor())
    @expose('spam.templates.forms.form2')
    def get_sendback(self, proj, asset_id, **kwargs):
        """Display a SENDBACK form."""
        asset = asset_get(proj, asset_id)

        f_status.custom_method = 'SENDBACK'
        f_status.value = dict(proj=asset.project.id,
                              asset_id=asset.id,
                              project_name_=asset.project.name,
                              container_=asset.parent.owner.path,
                              category_id_=asset.category.id,
                              asset_name_=asset.name,
                             )
                     
        tmpl_context.form = f_status
        return dict(title='%s: %s' % (_('Send back for revisions'), asset.path))

    @project_set_active
    @asset_set_active
    @require(is_asset_supervisor())
    @expose('json')
    @expose('spam.templates.forms.result')
    @validate(f_status, error_handler=get_submit)
    def post_sendback(self, proj, asset_id, comment=None):
        """Send back an asset for revision."""
        session = session_get()
        user = tmpl_context.user
        asset = asset_get(proj, asset_id)
        
        if asset.submitted and not asset.approved:
            asset.sendback(user)
            text = u'[%s v%03d]\n%s' % (_('sent back for revisions'),
                                            asset.current.ver, comment or '')
            asset.current.notes.append(Note(user, text))
            session.refresh(asset.current.annotable)

            # log into Journal
            journal.add(user, 'send back for revisions %s' % asset)
        
            # send a stomp message to notify clients
            notify.send(asset)
            notify.ancestors(asset)
            return dict(msg='asset "%s" sent back for revisions' % asset.path,
                                                            result='success')
        return dict(msg='asset "%s" cannot be sent back for revisions' %
                                                    asset.path, result='failed')

    @project_set_active
    @asset_set_active
    @require(is_asset_supervisor())
    @expose('spam.templates.forms.form2')
    def get_approve(self, proj, asset_id, **kwargs):
        """Display a APPROVE form."""
        asset = asset_get(proj, asset_id)

        f_status.custom_method = 'APPROVE'
        f_status.value = dict(proj=asset.project.id,
                              asset_id=asset.id,
                              project_name_=asset.project.name,
                              container_=asset.parent.owner.path,
                              category_id_=asset.category.id,
                              asset_name_=asset.name,
                             )
                     
        tmpl_context.form = f_status
        return dict(title='%s: %s' % (_('Approve'), asset.path))

    @project_set_active
    @asset_set_active
    @require(is_asset_supervisor())
    @expose('json')
    @expose('spam.templates.forms.result')
    @validate(f_status, error_handler=get_submit)
    def post_approve(self, proj, asset_id, comment=None):
        """Approve an asset submitted for approval."""
        session = session_get()
        user = tmpl_context.user
        asset = asset_get(proj, asset_id)
        
        if asset.submitted and not asset.approved:
            asset.approve(user)
            text = u'[%s v%03d]\n%s' % (_('approved'), asset.current.ver,
                                                                comment or '')
            asset.current.notes.append(Note(user, text))
            session.refresh(asset.current.annotable)

            # log into Journal
            journal.add(user, 'approved %s' % asset)
        
            # send a stomp message to notify clients
            notify.send(asset)
            notify.ancestors(asset)
            return dict(msg='approved asset "%s"' % asset.path,
                                                            result='success')
        return dict(msg='asset "%s" cannot be approved' % asset.path,
                                                            result='failed')

    @project_set_active
    @asset_set_active
    @require(is_asset_supervisor())
    @expose('spam.templates.forms.form2')
    def get_revoke(self, proj, asset_id, **kwargs):
        """Display a REVOKE form."""
        asset = asset_get(proj, asset_id)

        f_status.custom_method = 'REVOKE'
        f_status.value = dict(proj=asset.project.id,
                              asset_id=asset.id,
                              project_name_=asset.project.name,
                              container_=asset.parent.owner.path,
                              category_id_=asset.category.id,
                              asset_name_=asset.name,
                             )
                     
        tmpl_context.form = f_status
        return dict(title='%s: %s' % (_('Revoke approval for'), asset.path))

    @project_set_active
    @asset_set_active
    @require(is_asset_supervisor())
    @expose('json')
    @expose('spam.templates.forms.result')
    @validate(f_status, error_handler=get_submit)
    def post_revoke(self, proj, asset_id, comment=None):
        """Revoke approval for an asset."""
        session = session_get()
        user = tmpl_context.user
        asset = asset_get(proj, asset_id)
        
        if asset.approved:
            asset.revoke(user)
            text = u'[%s v%03d]\n%s' % (_('revoked approval'),
                                            asset.current.ver, comment or '')
            asset.current.notes.append(Note(user, text))
            session.refresh(asset.current.annotable)

            # log into Journal
            journal.add(user, 'revoked approval for %s' % asset)
        
            # send a stomp message to notify clients
            notify.send(asset)
            notify.ancestors(asset)
            return dict(msg='revoked approval for asset "%s"' % asset.path,
                                                            result='success')
        return dict(msg='approval for asset "%s" cannot be revoked' %
                                                    asset.path, result='failed')

    @project_set_active
    @require(is_project_user())
    @expose()
    def download(self, proj, assetver_id):
        """Return a version of an asset from the repository as a file 
        attachment in the response body."""
        assetver = assetversion_get(proj, assetver_id)
        f = repo.cat(proj, assetver)
        
        if assetver.asset.is_sequence:
            name = os.path.split(assetver.path)[0]
            path = '%s.zip' % name
        else:
            path = assetver.path
        
        # set the correct content-type so the browser will know what to do
        content_type, encoding = mimetypes.guess_type(path)
        response.headers['Content-Type'] = content_type
        response.headers['Content-Disposition'] = (
                                        ('attachment; filename=%s' %
                                            os.path.basename(path)).encode())
        
        # copy file content in the response body
        shutil.copyfileobj(f, response.body_file)
        f.close()
        return

