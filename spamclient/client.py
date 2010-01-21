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
"""Standalone SPAM client"""

import getpass, cookielib, urllib, urllib2, json
import project, scene, shot

class SPAMClient(object):
    """Standalone SPAM client."""
    
    def __init__(self, url):
        self.url = url.rstrip('/')
        
        self.project = project.Wrapper(self)
        self.scene = scene.Wrapper(self)
        self.shot = shot.Wrapper(self)
        
    def login(self, username, password=None):
        """Login in SPAM, and save an access cookie for subsequent commands.
        
        :Parameters:
            username : string
                your SPAM username
            password : string
                your password, if no password is given it will be asked at the
                command line
        """
        self.username = username
        if not password:
            password = getpass.getpass()
        credentials = urllib.urlencode(dict(login=username,
                                            password=password,
                                           )
                                      )
        cj = cookielib.CookieJar()
        self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
        url = '%s/login_handler?__logins=0&came_from=/' % self.url
        self.opener.open(url, credentials)
    
    def open(self, cmd, data=None):
        """Open a spam url using the builtin opener.
        
        You should not use "open" directly, use SPAMClient methods instead.

        :Parameters:
            cmd: string
                Command url without prefix (eg: '/project')
            data: string
                urlencoded POST data
        
        :Returns:
            a file-like object with the http response
        """
        #print('%s/%s' % (self.url, cmd.lstrip('/')), data)
        return self.opener.open('%s/%s' % (self.url, cmd.lstrip('/')), data)

