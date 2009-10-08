# -*- coding: utf-8 -*-
"""Main Controller"""

from tg import expose, flash, require, url, request, redirect, tmpl_context
from pylons.i18n import ugettext as _, lazy_ugettext as l_
from repoze.what import predicates

from spam.lib.base import SPAMBaseController
from spam.model import DBSession, metadata
from spam import model

__all__ = ['UserController']


class UserController(SPAMBaseController):
    """
    The user controller.
    
    """
    allow_only = predicates.not_anonymous(msg=l_('Please login'))
    
    @expose('spam.templates.user.home')
    def home(self):
        """Handle the 'home' page."""
        return dict(page="%s's home" % tmpl_context.user.user_name)


