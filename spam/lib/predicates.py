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
            if tmpl_context.project in tmpl_context.user.projects:
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
            if tmpl_context.project in tmpl_context.user.admin_projects:
                return
            if in_group('administrators'):
                return
        self.unmet()

