from tg import expose
from spam.lib.base import SPAMBaseController
from spam.controllers.admin.projects import ProjectsController

__all__ = ['AdminController']


class AdminController(SPAMBaseController):

    projects = ProjectsController()

