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
"""Shot module for the standalone SPAM client"""

import json, urllib
from utils import encode_params

class Wrapper(object):
    """Wrapper for the ``shot`` controller."""
    
    def __init__(self, client):
        self.client = client
    
    def get(self, proj, sc, sh):
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
        
        result = self.client.open('/shot/%s/%s/%s.json' % (proj, sc, sh))
        return json.loads(result.read())['shot']
    
    def new(self, proj, sc, sh, description=None, action=None, frames=None,
                                            handle_in=None, handle_out=None):
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
        data = encode_params(locals())
        
        return self.client.open('/shot.json', data)
    
    def edit(self, proj, sc, sh, description=None, action=None, frames=None,
                                            handle_in=None, handle_out=None):
        """Edit a shot.

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
        data = encode_params(locals(), _method='PUT')
        
        return self.client.open('/project.json', data)
    
    def delete(self, proj, sc ,sh):
        """Delete a project.
        
        Only delete the project record from the common db, the project
        repository must be removed manually.
        (This should help prevent awful accidents) ;)

        :Parameters:
            proj: string
                Project id (eg: 'dummy')
            sc: string
                Scene name (eg: 'sc01')
            sh: string
                Shot name (eg: 'sh01')
        """
        data = encode_params(locals(), _method='DELETE')
        
        return self.client.open('/project.json', data)

