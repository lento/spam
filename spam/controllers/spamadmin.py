from repoze.what.predicates import has_permission, in_group
from tgext.admin import AdminController, AdminConfig

class SPAMAdminConfig(AdminConfig):
    allow_only = in_group('administrators')
    include_left_menu = False

class SPAMAdminController(AdminController):
    allow_only = in_group('administrators')

