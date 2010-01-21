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
"""Scene module for the standalone SPAM client"""

import json, urllib
from utils import encode_params

class Wrapper(object):
    """Wrapper for the ``scene`` controller."""
    
    def __init__(self, client):
        self.client = client
    
    def get(self, proj, sc):
        """Get a scene.

        :Parameters:
            proj: string
                Project id (eg: 'dummy')
            sc: string
                Scene name (eg: 'sc01')

        :Returns:
            a ``scene`` dictionary
        """
        
        result = self.client.open('/scene/%s/%s.json' % (proj, sc))
        return json.loads(result.read())['scene']
    
    def new(self, proj, sc, description=None):
        """Create a new scene.

        :Parameters:
            proj: string
                Project id (eg: 'dummy')
            sc: string
                Scene name (eg: 'sc01')
            description: string
                Scene description (eg: 'dummy saves the day')
        """
        data = encode_params(locals())
        
        return self.client.open('/scene.json', data)
    
    def edit(self, proj, sc, description=None):
        """Edit a scene.

        :Parameters:
            proj: string
                Project id (eg: 'dummy')
            sc: string
                Scene name (eg: 'sc01')
            description: string
                Scene description (eg: 'dummy saves the day')
        """
        data = encode_params(locals(), _method='PUT')
        
        return self.client.open('/project.json', data)
    
    def delete(self, proj, sc):
        """Delete a scene.
        
        Only delete the scene record from the db, the scene directories must be
        removed manually.
        (This should help prevent awful accidents) ;)

        :Parameters:
            proj: string
                Project id (eg: 'dummy')
            sc: string
                Scene name (eg: 'sc01')
        """
        data = encode_params(locals(), _method='DELETE')
        
        return self.client.open('/project.json', data)

