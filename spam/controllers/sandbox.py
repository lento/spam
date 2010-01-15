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
"""Sandbox controller"""

import logging, os
from tg import request
from tg import url, expose, validate, tmpl_context
from spam.lib.base import SPAMBaseController
from spam.lib.widgets import FormProjectEdit
from spam.lib.widgets import TableScenes
from spam.lib.widgets import ListTags
from spam.model import project_get, shot_get

t_scenes = TableScenes()
l_tags = ListTags()

log = logging.getLogger(__name__)
f_project_edit = FormProjectEdit(action=url('/test/putvalidation'))

class SandboxController(SPAMBaseController):
    """A testing and debugging environment.
    
    Sandbox methods are just quick tests for new features or for debugging
    errors.
    """
    
    @expose('spam.templates.forms.form')
    def validation(self, proj, **kwargs):
        log.debug('validation: %s', kwargs)
        tmpl_context.form = f_project_edit
        
        fargs = dict()
        fcargs = dict()
        return dict(title='test project edit', args=fargs, child_args=fcargs)
    
    @expose('spam.templates.forms.result')
    @validate(form=f_project_edit)
    def putvalidation(self, **kwargs):
        log.debug('putvalidation: kwargs=%s - errors=%s' %
                                    (kwargs, tmpl_context.form_errors or None))
        return dict(msg='form received with kwargs: %s- errors=%s' %
                                    (kwargs, tmpl_context.form_errors or None),
                                    result='success')

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

    @expose('spam.templates.sandbox.taglist')
    def taglist(self, proj, sc, sh):
        tmpl_context.l_tags = l_tags
        shot = shot_get(proj, sc, sh)
        tags = shot.tags
        return dict(page='sandbox/taglist', shot=shot, tags=tags)

    @expose('spam.templates.sandbox.livetable')
    def livetable(self):
        from spam.lib.widgets import TableTest
        t_test = TableTest()
        items = [dict(a='one', b=1), dict(a='two', b=2)]
        tmpl_context.t_test = t_test
        return dict(items=items)
        
