# -*- coding: utf-8 -*-
"""Main Controller"""
import os.path, datetime

from tg import expose, flash, require, url, request, redirect, override_template
from tg import response, config, app_globals, tmpl_context
from tg.exceptions import HTTPNotFound
from pylons.i18n import ugettext as _, lazy_ugettext as l_
from repoze.what.predicates import not_anonymous

from spam.lib.base import SPAMBaseController
from spam.model import User, Group, Permission, Project
from spam.controllers.error import ErrorController
from spam.controllers.user import UserController
from spam.controllers.sandbox import SandboxController
from spam.controllers import project, scene, shot, asset, category, libgroup


__all__ = ['RootController']


class RootController(SPAMBaseController):
    """
    The root controller for the SPAM application.
    
    All the other controllers and WSGI applications should be mounted on this
    controller. For example::
    
        panel = ControlPanelController()
        another_app = AnotherWSGIApplication()
    
    Keep in mind that WSGI applications shouldn't be mounted directly: They
    must be wrapped around with :class:`tg.controllers.WSGIAppController`.
    """
    error = ErrorController()
    user = UserController()
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
        scriptname = os.path.splitext(script)[0]
        templatename = 'spam.templates.parsedjs.%s' % scriptname
        
        if config.get('use_dotted_templatenames', False):
            template = app_globals.dotted_filename_finder.get_dotted_filename(
                                    templatename, template_extension='.mak')
            if not os.path.exists(template):
                raise HTTPNotFound
        
        override_template(self.parsedjs, 'mako:%s' % templatename)

        return dict()

