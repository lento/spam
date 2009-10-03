from tg import url, expose, tmpl_context
from spam.lib.base import SPAMBaseController
from spam.lib.widgets import FormNewProject

__all__ = ['FormController']

f_new_project = FormNewProject(action=url('/admin/projects/create_project'))

class FormController(SPAMBaseController):

    @expose('spam.templates.form')
    def new_project(self, **kwargs):
        tmpl_context.form = f_new_project
        fargs = dict()
        fcargs = dict()
        return dict(title='Create a new project', args=fargs, child_args=fcargs)


