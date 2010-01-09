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


class SPAMClient(object):
    """Standalone SPAM client."""
    def __init__(self, url):
        self.url = url.rstrip('/')
        
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
    
    def project_new(self, proj, name=None, description=None):
        """Create a new project.

        :Parameters:
            proj: string
                Project id (eg: 'dummy')
            name: string
                Project display name (eg: 'Dummy Returns')
            description: string
                Project description (eg: 'A test project')
        
        :Returns:
            a ``project`` object
        """
        data = urllib.urlencode(dict(proj=proj,
                                     name=name,
                                     description=description,
                                    ))
        
        result = self.open('/project.json', data)
    
    def project_get(self, proj):
        """Get a project.

        :Parameters:
            proj: string
                Project id (eg: 'dummy')

        :Returns:
            a ``project`` dictionary
        """
        
        result = self.open('/project/%s.json' % proj)
        return json.loads(result.read())['project']
    
    def scene_new(self, proj, sc, description=None):
        """Create a new scene.

        :Parameters:
            proj: string
                Project id (eg: 'dummy')
            sc: string
                Scene name (eg: 'sc01')
            description: string
                Scene description (eg: 'dummy saves the day')
        """
        data = urllib.urlencode(dict(proj=proj,
                                     sc=sc,
                                     description=description,
                                    ))
        
        result = self.open('/scene.json', data)
    
    def scene_get(self, proj, sc):
        """Get a scene.

        :Parameters:
            proj: string
                Project id (eg: 'dummy')
            sc: string
                Scene name (eg: 'sc01')

        :Returns:
            a ``scene`` dictionary
        """
        
        result = self.open('/scene/%s/%s.json' % (proj, sc))
        return json.loads(result.read())['scene']
    
    def shot_new(self, proj, sc, sh, description=None, action=None, frames=0,
                                                    handle_in=0, handle_out=0):
        """Create a new shot.

        :Parameters:
            proj: string
                Project id (eg: 'dummy')
            sc: string
                Scene name (eg: 'sc01')
            sh: string
                Shot name (eg: 'sh01')
            description: string
                Shot description (eg: "close-up on dummy's smile")
            action: string
                Shot action (eg: "dummy smiles while saving the day")
            frames: int
                Shot lenght in frames
            handle_in: int
                Handle frames at the start of the shot
            handle_out: int
                Handle_out: Handle frames at the end of the shot
        """
        data = urllib.urlencode(dict(proj=proj,
                                     sc=sc,
                                     sh=sh,
                                     description=description,
                                     action=action,
                                     frames=frames,
                                     handle_in=handle_in,
                                     handle_out=handle_out,
                                    ))
        
        result = self.open('/shot.json', data)
    
    def shot_get(self, proj, sc, sh):
        """Get a shot.

        :Parameters:
            proj: string
                Project id (eg: 'dummy')
            sc: string
                Scene name (eg: 'sc01')
            sh: string
                Shot name (eg: 'sh01')

        :Returns:
            a ``shot`` dictionary
        """
        
        result = self.open('/shot/%s/%s/%s.json' % (proj, sc, sh))
        return json.loads(result.read())['shot']
    
    
