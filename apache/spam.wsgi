import os, sys, site
sys.stdout = sys.stderr

#import site
site.addsitedir('/home/lorenzo/dev/virtualenv/tg2env/lib/python2.6/site-packages')

#new_sys_path = []
#for item in list(sys.path):
#    if item not in prev_sys_path:
#        new_sys_path.append(item)
#        sys.path.remove(item)
#sys.path[:0] = new_sys_path 

#import os, sys

sys.path.append('/home/lorenzo/dev/mrApps/spam')
os.environ['PYTHON_EGG_CACHE'] = '/var/www/wsgi/python-eggs'

from paste.deploy import loadapp

application = loadapp('config:/home/lorenzo/dev/mrApps/spam/apache.ini')
