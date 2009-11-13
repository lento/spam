import tg
from tw.api import Widget, WidgetsList, JSLink
from tw.forms import TableForm, TextField, TextArea
from tw.forms.validators import All, Regex, MaxLength
from spam.lib.repo import pattern_nick
from spam.lib.twlib.livetable import LiveTable, IconButton

spam_js = JSLink(link=tg.url('/parsedjs/spam.js'))

# JQuery and plugins
jquery_js = JSLink(link=tg.url('/js/jquery.js'))
overlay_js = JSLink(link=tg.url('/js/tools.overlay.js'))
jquery_cookie_js = JSLink(link=tg.url('/js/jquery.cookie.js'))
jquery_treeview_js = JSLink(link=tg.url('/js/jquery.treeview.js'))


class StartupJS(Widget):
    javascript = [jquery_js, spam_js, overlay_js, jquery_cookie_js,
                  jquery_treeview_js]


# Live tables
class ActiveProjects(LiveTable):
    class buttons(WidgetsList):
        edit = IconButton(icon_class='edit')
        archive = IconButton(icon_class='archive')

class ArchivedProjects(LiveTable):
    class buttons(WidgetsList):
        reactivate = IconButton(icon_class='activate')


# Form widgets
class FormNewProject(TableForm):
    class fields(WidgetsList):
        nick = TextField(validator=All(Regex(pattern_nick, not_empty=True),
                                                                MaxLength(15)))
        name = TextField(validator=MaxLength(40))
        description = TextArea(cols=30, rows=3)


