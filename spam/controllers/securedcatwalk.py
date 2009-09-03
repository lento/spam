from catwalk.tg2 import Catwalk
from repoze.what.predicates import in_group

class SecuredCatwalk(Catwalk):
    allow_only = in_group('administrators')
