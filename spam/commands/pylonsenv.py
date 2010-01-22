import os
import sys
import pkg_resources
import paste.fixture, paste.registry
from paste.deploy import loadapp

def setup():
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

