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
"""Utils for the standalone SPAM client"""

import urllib

def encode_params(args, **kwargs):
    del args['self']
    
    params = dict()
    for key, value in args.iteritems():
        if value is not None:
            params[key] = value
        else:
            params[key] = ''
    
    for key, value in kwargs.iteritems():
        if value is not None:
            params[key] = value
        else:
            params[key] = ''
    
    encoded = urllib.urlencode(params)
    
    return encoded

