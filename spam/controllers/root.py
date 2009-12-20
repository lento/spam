# -*- coding: utf-8 -*-
#
# SPAM Spark Project & Asset Manager
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
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
# Copyright (c) 2009, Lorenzo Pierfederici <lpierfederici@gmail.com>
# Contributor(s): 
#
"""Main Controller"""

import os.path, datetime, shutil, mimetypes

from tg import expose, flash, require, url, request, redirect, override_template
from tg import response, config, tmpl_context, app_globals as G
from tg.exceptions import HTTPNotFound
from tg.controllers import CUSTOM_CONTENT_TYPE
from pylons.i18n import ugettext as _, lazy_ugettext as l_
from repoze.what.predicates import not_anonymous

from spam.lib.base import SPAMBaseController
from spam.model import User, Group, Permission, Project
from spam.controllers.error import ErrorController
from spam.controllers.sandbox import SandboxController
from spam.controllers import user, category
from spam.controllers import project, scene, shot, asset, libgroup
from spam.lib.decorators import project_set_active
from spam.lib.predicates import is_project_user, is_project_admin


__all__ = ['RootController']


class RootController(SPAMBaseController):
    """
    The root controller for the SPAM application.
    
    It manages login and logout, parsed javascripts and upload-to/download-from
    the projects repository.
    All other functionalities are mounted as subcontrollers.
    """
    
    error = ErrorController()
    user = user.Controller()
    sandbox = SandboxController()
    project = project.Controller()
    scene = scene.Controller()
    shot = shot.Controller()
    asset = asset.Controller()
    category = category.Controller()
    libgroup = libgroup.Controller()
    
    @expose()
    def index(self):
        """Redirect to the user home.
        
        If no user is logged in it will fire up the login form.
        """
        redirect('/user/home')

    @expose('spam.templates.login')
    def login(self, came_from=url('/')):
        """Start the user login."""
        login_counter = request.environ['repoze.who.logins']
        if login_counter > 0:
            flash(_('Wrong credentials'), 'warning')
        return dict(page='login', login_counter=str(login_counter),
                    came_from=came_from)
    
    @expose()
    def post_login(self, came_from=url('/')):
        """
        Redirect the user to the initially requested page on successful
        authentication or redirect her back to the login page if login failed.
        """
        if not request.identity:
            login_counter = request.environ['repoze.who.logins'] + 1
            redirect(url('/login', came_from=came_from, __logins=login_counter))
        userid = request.identity['repoze.who.userid']
        flash(_('Welcome back, %s!') % userid)
        redirect(came_from)

    @expose()
    def post_logout(self, came_from=url('/')):
        """
        Redirect the user to the initially requested page on logout and say
        goodbye as well.
        """
        flash(_('See you soon!'))
        redirect(came_from)
    
    @expose(content_type='text/javascript')
    @require(not_anonymous(msg=l_('Please login')))
    def parsedjs(self, script, *args, **kwargs):
        """
        Render the required javascript from a template of the same name (but
        with a .mak extension) as found in spam/templates/parsedjs/
        
        This is needed for javascripts that use config variables from spam or
        other variable data.
        """
        scriptname = os.path.splitext(script)[0]
        templatename = 'spam.templates.parsedjs.%s' % scriptname
        
        if config.get('use_dotted_templatenames', False):
            template = G.dotted_filename_finder.get_dotted_filename(
                                    templatename, template_extension='.mak')
            if not os.path.exists(template):
                raise HTTPNotFound
        
        override_template(self.parsedjs, 'mako:%s' % templatename)

        return dict()

    @expose('spam.templates.sandbox.upload')
    @require(not_anonymous(msg=l_('Please login')))
    def upload(self, uploadedfile):
        """
        Upload a file (or a list of files) to a temporary storage area as a
        first step for publishing an asset. The file can then be moved to the
        repository and versioned with the asset controller's "publish" method. 
        
        The path for this storage area can be configured in the .ini file with
        the "upload_dir" variable.
        """
        if isinstance(uploadedfile, list):
            for uf in uploadedfile:
                tmpf = open(os.path.join(G.UPLOAD, uf.filename), 'w+b')
                tmpf.write(uf.file.read())
                tmpf.close()
        else:
            tmpf = open(os.path.join(G.UPLOAD, uploadedfile.filename), 'w+b')
            tmpf.write(uploadedfile.file.read())
            tmpf.close()
        return dict()

    @project_set_active
    @require(is_project_user())
    @expose(content_type=CUSTOM_CONTENT_TYPE)
    def repo(self, *args):
        """
        Return a file from the repository. We retrive file like that instead of
        serving them statically so we can use authorization (a project file can
        only be requested by a valid project user).

        The path for the projects repository can be configured in the .ini file
        with the "repository" variable.
        """
        path = request.path
        path = path.replace(url('/'), '')
        path = path.replace('repo/', '')
        path = os.path.join(G.REPOSITORY, path)
        if not os.path.exists(path):
            raise HTTPNotFound().exception
        
        # set the correct content-type so the browser will know what to do
        content_type, encoding = mimetypes.guess_type(path)
        response.headers['Content-Type'] = content_type
        response.headers['Content-Disposition'] = (
                ('attachment; filename=%s' % os.path.basename(path)).encode())
        
        # copy file content in the response body
        f = open(path)
        shutil.copyfileobj(f, response.body_file)
        f.close()
        return

