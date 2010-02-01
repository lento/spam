""" Custom decorators for SPAM.
"""
from decorator import decorator
from tg import tmpl_context, request
from spam.model import session_get, project_get, asset_get
from spam.lib.exceptions import SPAMError

import logging
log = logging.getLogger(__name__)

@decorator
def project_set_active(func, *args, **kwargs):
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
    if 'asset_id' in kwargs:
        asset_id = kwargs['asset_id']
    elif len(args)>2:
        asset_id = args[2]
    else:
        raise SPAMError('No asset_id defined')

    project = tmpl_context.project
    tmpl_context.asset = asset_get(project.id, asset_id)
    return func(*args, **kwargs)
    

