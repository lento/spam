from tg import expose
from spam.lib.base import SPAMBaseController

__all__ = ['AdminController']


class AdminController(SPAMBaseController):

    @expose('spam.templates.admin.project')
    def project(self):
        return dict(title='Admin Project')

