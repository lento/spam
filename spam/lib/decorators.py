""" Custom decorators for SPAM.
"""
from decorator import decorator
from tg import tmpl_context, request
from spam.model import session_get, project_get
from spam.lib.exceptions import SPAMError

import logging
log = logging.getLogger(__name__)

@decorator
def project_set_active(func, *args, **kwargs):
    session = session_get()
    if 'proj' in kwargs:
        proj = kwargs['proj']
    elif len(args)>1:
        proj = args[1]
    else:
        raise SPAMError('No project defined')

    tmpl_context.project = project_get(proj)
    return func(*args, **kwargs)
    

