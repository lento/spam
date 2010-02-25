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
"""Pylons environment utilities."""

import os
import sys
import pkg_resources
import paste.fixture, paste.registry
from paste.deploy import loadapp

def setup():
    """Setup a pylons environment and populates StackedProxy objects."""
    global pylonsapp
    path = os.getcwd()
    sys.path.insert(0, path)
    pkg_resources.working_set.add_entry(path)

    # Load the wsgi app first so that everything is initialized right
    wsgiapp = loadapp('config:development.ini', relative_to=path)
    test_app = paste.fixture.TestApp(wsgiapp)

    # Query the test app to setup the environment
    tresponse = test_app.get('/_test_vars')
    request_id = int(tresponse.body)

    # Restore the state of the Pylons special objects
    # (StackedObjectProxies)
    paste.registry.restorer.restoration_begin(request_id)

