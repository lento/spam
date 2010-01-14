from spam.model import session_get, Journal
from spam.lib.notifications import notify


class Journaler(object):
    def add(self, user, text):
        entry = Journal(user, text)
        session_get().add(entry)
        notify.send(entry, update_type='added')

journal = Journaler()
