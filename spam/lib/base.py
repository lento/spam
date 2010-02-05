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
"""The base Controller API."""

from tg import TGController, tmpl_context, config
from tg.render import render
from tg import request
from pylons.i18n import _, ungettext, N_
from tw.api import WidgetBunch
import spam.model as model
from spam.lib.widgets import StartupJS, NetworkingJS, NotifyClientJS
from spam.lib.widgets import ListProjects
from spam.lib import predicates 

j_networking = NetworkingJS()
j_startup = StartupJS()
j_notify_client = NotifyClientJS()
l_projects = ListProjects()


class BaseController(TGController):
    """Base class for the controllers in the application.

    Your web application should have one of these. The root of
    your application is used to compute URLs used by your app.
    """

    def __call__(self, environ, start_response):
        """Invoke the Controller"""
        # TGController.__call__ dispatches to the Controller method
        # the request is routed to. This routing information is
        # available in environ['pylons.routes_dict']

        request.identity = request.environ.get('repoze.who.identity')
        tmpl_context.identity = request.identity
        return TGController.__call__(self, environ, start_response)


class SPAMBaseController(TGController):
    """ Base class for the controllers in SPAM.

    This base controller initialize and expose some items to templates.
    """
    def __call__(self, environ, start_response):
        """Invoke the Controller"""
        # TGController.__call__ dispatches to the Controller method
        # the request is routed to. This routing information is
        # available in environ['pylons.routes_dict']

        request.identity = request.environ.get('repoze.who.identity')
        tmpl_context.identity = request.identity
        if request.identity:
            tmpl_context.user = request.identity['user']
        
        # set the theme
        tmpl_context.theme = config.get('theme', 'default')
        
        # load javascripts
        tmpl_context.j_networking = j_networking
        tmpl_context.j_startup = j_startup
        tmpl_context.j_notify_client = j_notify_client
        tmpl_context.l_projects = l_projects
        
        # custom predicates
        tmpl_context.predicates = predicates
        
        return TGController.__call__(self, environ, start_response)


