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
"""Project module for the standalone SPAM client"""

import json, urllib
from utils import encode_params

class Wrapper(object):
    """Wrapper for the ``project`` controller."""
    
    def __init__(self, client):
        self.client = client
    
    def get(self, proj):
        """Get a project.

        :Parameters:
            proj: string
                Project id (eg: 'dummy')

        :Returns:
            a ``project`` dictionary
        """
        
        result = self.client.open('/project/%s.json' % proj)
        return json.loads(result.read())['project']
    
    def new(self, proj, name=None, description=None):
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
        data = encode_params(locals())
        
        return self.client.open('/project.json', data)
    
    def edit(self, proj, name=None, description=None):
        """Edit a project.

        :Parameters:
            proj: string
                Project id (eg: 'dummy')
            name: string
                Project display name (eg: 'Dummy Returns')
            description: string
                Project description (eg: 'A test project')
        """
        data = encode_params(locals(), _method='PUT')
        
        return self.client.open('/project.json', data)
    
    def delete(self, proj):
        """Delete a project.
        
        Only delete the project record from the common db, the project
        repository must be removed manually.
        (This should help prevent awful accidents) ;)

        :Parameters:
            proj: string
                Project id (eg: 'dummy')
        """
        data = encode_params(locals(), _method='DELETE')
        
        return self.client.open('/project.json', data)
    
    def archive(self, proj):
        """Archive a project.
        
        :Parameters:
            proj: string
                Project id (eg: 'dummy')
        """
        data = encode_params(locals(), _method='ARCHIVE')
        
        return self.client.open('/project.json', data)
    
    def activate(self, proj):
        """Activate a project.
        
        :Parameters:
            proj: string
                Project id (eg: 'dummy')
        """
        data = encode_params(locals(), _method='ACTIVATE')
        
        return self.client.open('/project.json', data)
    

