ALLDIRS = ['/home/lorenzo/dev/virtualenv/tg21env/lib/python2.6/site-packages']

import sys 
import site 
sys.stdout = sys.stderr

# Remember original sys.path.
#prev_sys_path = list(sys.path) 

# Add each new site-packages directory.
for directory in ALLDIRS:
  site.addsitedir(directory)

# Reorder sys.path so new directories at the front.
#new_sys_path = [] 
#for item in list(sys.path): 
#    if item not in prev_sys_path: 
#        new_sys_path.append(item) 
#        sys.path.remove(item) 
#sys.path[:0] = new_sys_path

import os
os.environ['PYTHON_EGG_CACHE'] = '/var/www/wsgi/python-eggs'

from paste.deploy import loadapp
application = loadapp('config:/var/www/wsgi/apps/spam/deployment.ini')

# init the app by calling '/' to be sure that all threads register toscawidgets
# and their resources
import paste.fixture
app = paste.fixture.TestApp(application)
app.get("/")

