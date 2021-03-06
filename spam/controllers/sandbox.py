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
"""Sandbox controller"""

import logging, os, time
from tg import request
from tg import url, expose, validate, tmpl_context
from spam.lib.base import SPAMBaseController
from spam.lib.widgets import TableScenes
from spam.model import project_get, shot_get, session_get, User
from spam.lib.widgets import TableUsers, TableGroupUsers

t_users = TableUsers(id='t_users')
t_scenes = TableScenes()

log = logging.getLogger(__name__)

class SandboxController(SPAMBaseController):
    """A testing and debugging environment.
    
    Sandbox methods are just quick tests for new features or for debugging
    errors.
    """
    
    @expose('spam.templates.sandbox.stomp')
    def stomp(self):
        return dict(page='sandbox/stomp')

    @expose('spam.templates.sandbox.location')
    def location(self, *args, **kwargs):
        return dict(page='sandbox/location', args=args, kwargs=kwargs)
    
    @expose('spam.templates.sandbox.scenes')
    def scenes(self, proj):
        project = project_get(proj)
        tmpl_context.t_scenes = t_scenes
        return dict(scenes=project.scenes)
    
    @expose('spam.templates.sandbox.publish')
    def publish(self):
        return dict()
    
    @expose('spam.templates.sandbox.upload')
    def upload(self, uploadedfile):
        log.debug('sandbox upload(): %s' % (uploadedfile))
        #tmpfd, tmpname = tempfile.mkstemp()
        #tmpf = os.fdopen(tmpfd, 'w+b')
        if isinstance(uploadedfile, list):
            for uf in uploadedfile:
                tmpf = open('/home/lorenzo/Desktop/upload/%s' % uf.filename, 'w+b')
                tmpf.write(uf.file.read())
                tmpf.close()
        else:
            tmpf = open('/home/lorenzo/Desktop/upload/%s' % uploadedfile.filename, 'w+b')
            tmpf.write(uploadedfile.file.read())
            #tmpf.write(request.body_file.read())
            tmpf.close()
        return dict()

    @expose('spam.templates.sandbox.update')
    def update(self):
        users = session_get().query(User).all()
        t_users.value = users
        t_users.update_topic = 'users'
        tmpl_context.t_users = t_users
        return dict(users=users)

    @expose('spam.templates.sandbox.dialog')
    def dialog(self):
        return dict()

    @expose()
    def echo(self, **kw):
        time.sleep(5)
        return kw

