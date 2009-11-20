import logging
from tg import url, expose, validate, tmpl_context
from spam.lib.base import SPAMBaseController
from spam.lib.widgets import FormProjectEdit

log = logging.getLogger(__name__)
f_project_edit = FormProjectEdit(action=url('/test/putvalidation'))

class SandboxController(SPAMBaseController):
    """A testing and debugging environment"""
    
    @expose('spam.templates.forms.form')
    def validation(self, proj, **kwargs):
        log.debug('validation: %s', kwargs)
        tmpl_context.form = f_project_edit
        
        fargs = dict()
        fcargs = dict()
        return dict(title='test project edit', args=fargs, child_args=fcargs)
    
    @expose('spam.templates.forms.result')
    @validate(form=f_project_edit)
    def putvalidation(self, **kwargs):
        log.debug('putvalidation: kwargs=%s - errors=%s' %
                                    (kwargs, tmpl_context.form_errors or None))
        return dict(msg='form received with kwargs: %s- errors=%s' %
                                    (kwargs, tmpl_context.form_errors or None),
                                    result='success')


