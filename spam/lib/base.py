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
"""The base Controller API."""

from tg import TGController, tmpl_context, config, url
from tg.render import render
from tg import request
from pylons.i18n import _, ungettext, N_
from tw.api import WidgetBunch, JSLink
import spam.model as model
from spam.lib.widgets import ListProjects
from spam.lib import predicates 

# Orbited
orbited_address = config.get('orbited_address', 'http://localhost:9000')

orbited_js = JSLink(link='%s/static/Orbited.js' % orbited_address)
initsocket_js = JSLink(link=url('/js/init_TCPSocket.js'))
stomp_js = JSLink(link='%s/static/protocols/stomp/stomp.js' % orbited_address)

# JQuery and plugins
jquery_spamkit_js = JSLink(link=url('/js/jquery.spamkit.js.gz'))
#jquery_tablesorter_js = JSLink(link=url('/js/jquery.tablesorter.js'))

# SPAM
spam_js = JSLink(link=url('/js/spam.js'))
notify_client_js = JSLink(link=url('/js/notify_client.js'))

# widgets
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
#        orbited_js.inject()
#        initsocket_js.inject()
#        stomp_js.inject()

        jquery_spamkit_js.inject()
#        jquery_tablesorter_js.inject()

        spam_js.inject()
        notify_client_js.inject()

        # widgets
        tmpl_context.l_projects = l_projects

        # custom predicates
        tmpl_context.predicates = predicates

        return TGController.__call__(self, environ, start_response)


