# -*- coding: utf-8 -*-
"""
    :copyright: 2009 by Toshio Kuratomi <tkuratom@redhat.com>
                Adapted by code from pylons testutil.py,
                Copyright (c) 2005-2009 Ben Bangert, James Gardner,
                    Philip Jenvey and contributors.
    :license: BSD (same as testutil.py code)
    
    modified by Lorenzo Pierfederici <lpierfederici@gmail.com>
"""
import os
import sys
import pkg_resources
from sphinx.builders import Builder
import paste.fixture, paste.registry
from paste.deploy import loadapp
from pylons.i18n.translation import _get_translator
from pylons.controllers.util import Request
import pylons
import routes
try:
    import tw.forms.validators
except ImportError:
    pass
else:
    tw.forms.validators.Validator.gettextargs = {}

pylonsapp = None
class PylonsSetup(Builder):
    """Pylons environment helper."""
    @classmethod
    def pylons_env_setup(cls, app):
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

def setup(app):
    """Setup a pylons environment."""
    PylonsSetup.pylons_env_setup(app)
    app.add_config_value('pylons_config_file', '', None)

    #app.connect('builder-inited', builder_inited)
