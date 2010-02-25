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
""" Custom decorators for SPAM."""

from decorator import decorator
from tg import tmpl_context, request
from spam.model import session_get, project_get, asset_get
from spam.lib.exceptions import SPAMError

import logging
log = logging.getLogger(__name__)

@decorator
def project_set_active(func, *args, **kwargs):
    """Extract the current project id from the args passed to the function
    and puts the corresponding project in the template context.
    
    If the project id is not valid raise an error."""
    if 'proj' in kwargs:
        proj = kwargs['proj']
    elif len(args)>1:
        proj = args[1]
    else:
        raise SPAMError('No project defined')

    tmpl_context.project = project_get(proj)
    return func(*args, **kwargs)
    
@decorator
def asset_set_active(func, *args, **kwargs):
    """Extract the current asset id from the args passed to the function
    and puts the corresponding asset in the template context.
    
    If the asset id is not valid raise an error."""
    if 'asset_id' in kwargs:
        asset_id = kwargs['asset_id']
    elif len(args)>2:
        asset_id = args[2]
    else:
        raise SPAMError('No asset_id defined')

    project = tmpl_context.project
    tmpl_context.asset = asset_get(project.id, asset_id)
    return func(*args, **kwargs)
    

