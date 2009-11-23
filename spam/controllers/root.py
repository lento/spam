# -*- coding: utf-8 -*-
"""Main Controller"""
import os.path, datetime

from tg import expose, flash, require, url, request, redirect, override_template
from tg import response, config, app_globals
from tg.exceptions import HTTPNotFound
from pylons.i18n import ugettext as _, lazy_ugettext as l_
from repoze.what import predicates

from spam.lib.base import SPAMBaseController
from spam.model import DBSession, metadata, get_project_eager
from spam.model import User, Group, Permission, Project
from spam.controllers.error import ErrorController
from spam.controllers.user import UserController
from spam.controllers.form import FormController
from spam.controllers.project import ProjectController
from spam.controllers.sandbox import SandboxController


__all__ = ['RootController']


class RootController(SPAMBaseController):
    """
    The root controller for the spam application.
    
    All the other controllers and WSGI applications should be mounted on this
    controller. For example::
    
        panel = ControlPanelController()
        another_app = AnotherWSGIApplication()
    
    Keep in mind that WSGI applications shouldn't be mounted directly: They
    must be wrapped around with :class:`tg.controllers.WSGIAppController`.
    
    """
    error = ErrorController()
    user = UserController()
    form = FormController()
    project = ProjectController()
    sandbox = SandboxController()
    
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
    def parsedjs(self, script):
        scriptname = os.path.splitext(script)[0]
        templatename = 'spam.templates.parsedjs.%s' % scriptname
        
        if config.get('use_dotted_templatenames', False):
            template = app_globals.dotted_filename_finder.get_dotted_filename(
                                    templatename, template_extension='.mak')
            if not os.path.exists(template):
                raise HTTPNotFound
        
        override_template(self.parsedjs, 'mako:%s' % templatename)

        return dict()

    @expose('spam.templates.view.scene')
    def scene(self, proj, sc):
        project = get_project_eager(proj)
        scene = [s for s in project.scenes if s.name==sc][0]
        
        return dict(page='scene view', project=project, scene=scene,
                                            sidebar=('projects', project.id))


    @expose('spam.templates.view.shot')
    def shot(self, proj, sc, sh):
        project = get_project_eager(proj)
        scene = [s for s in project.scenes if s.name==sc][0]
        shot = [h for h in scene.shots if h.name==sh][0]
        
        return dict(page='shot view', project=project, scene=scene, shot=shot,
                                            sidebar=('projects', project.id))


