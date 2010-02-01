from tg import tmpl_context
from repoze.what.predicates import Predicate, in_group

import logging
log = logging.getLogger(__name__)

class is_project_user(Predicate):
    """Predicate for checking whether the visitor is a valid  project user.
    
    This predicate requires the "project_set_active" decorator earlier in the
    stack, because it relies on tmpl_context.project to be set.
    """
    message = (u'The user must be a valid user for this project')

    def evaluate(self, environ, credentials):
        if hasattr(tmpl_context, 'user') and hasattr(tmpl_context, 'project'):
            userid = credentials.get('repoze.what.userid')
            if tmpl_context.user in tmpl_context.project.users:
                return
            if in_group('administrators'):
                return
        self.unmet()

class is_project_admin(Predicate):
    """Predicate for checking whether the visitor is an administrator of the
    current project.
    
    This predicate requires the "project_set_active" decorator earlier in the
    stack, because it relies on tmpl_context.project to be set.
    """
    message = (u'The user must be a project administrator')

    def evaluate(self, environ, credentials):
        if hasattr(tmpl_context, 'user') and hasattr(tmpl_context, 'project'):
            userid = credentials.get('repoze.what.userid')
            if tmpl_context.user in tmpl_context.project.admins:
                return
            elif in_group('administrators'):
                return
        self.unmet()

class is_asset_supervisor(Predicate):
    """Predicate for checking whether the visitor is a supervisor for the
    given asset.
    
    This predicate requires "project_set_active" and "asset_set_active"
    decorators earlier in the stack, because it relies on tmpl_context.project
    and tmpl_context.asset to be set.
    """
    message = (u'The user must be registered as "supervisor"')

    def evaluate(self, environ, credentials):
        if hasattr(tmpl_context, 'user') and hasattr(tmpl_context, 'project'):
            userid = credentials.get('repoze.what.userid')
            if tmpl_context.user in tmpl_context.asset.supervisors:
                return
            elif tmpl_context.user in tmpl_context.project.admins:
                return
            elif in_group('administrators'):
                return
        self.unmet()

class is_asset_artist(Predicate):
    """Predicate for checking whether the visitor is an artist for the given
    asset.
    
    This predicate requires "project_set_active" and "asset_set_active"
    decorators earlier in the stack, because it relies on tmpl_context.project
    and tmpl_context.asset to be set.
    """
    message = (u'The user must be registered as "artist"')

    def evaluate(self, environ, credentials):
        if hasattr(tmpl_context, 'user') and hasattr(tmpl_context, 'project'):
            userid = credentials.get('repoze.what.userid')
            if tmpl_context.user in tmpl_context.asset.artist:
                return
            elif tmpl_context.user in tmpl_context.project.admins:
                return
            elif in_group('administrators'):
                return
        self.unmet()

class is_asset_owner(Predicate):
    """Predicate for checking whether the visitor is the owner of the given
    asset.
    
    This predicate requires "project_set_active" and "asset_set_active"
    decorators earlier in the stack, because it relies on tmpl_context.project
    and tmpl_context.asset to be set.
    """
    message = (u'The user must be the owner')

    def evaluate(self, environ, credentials):
        if hasattr(tmpl_context, 'user') and hasattr(tmpl_context, 'project'):
            userid = credentials.get('repoze.what.userid')
            if tmpl_context.user is tmpl_context.asset.owner:
                return
        self.unmet()

