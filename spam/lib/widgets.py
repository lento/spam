import tg
from tw.api import Widget, WidgetsList, JSLink
from tw import forms
from tw.forms.validators import All, Regex, MaxLength
from spam.lib.repo import pattern_nick
from spam.lib.twlib import livetable as lt

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
class ActiveProjects(lt.LiveTable):
    class fields(WidgetsList):
        edit = lt.IconButton(icon_class='edit')
        archive = lt.IconButton(icon_class='archive')
        id = lt.TextField()
        name = lt.TextField()
        description = lt.TextField()
        created = lt.TextField()

class ArchivedProjects(lt.LiveTable):
    class fields(WidgetsList):
        reactivate = lt.IconButton(icon_class='activate')
        id = lt.TextField()
        name = lt.TextField()
        description = lt.TextField()
        created = lt.TextField()


# Form widgets
class FormNewProject(forms.TableForm):
    class fields(WidgetsList):
        nick = forms.TextField(validator=All(Regex(pattern_nick,
                                                not_empty=True), MaxLength(15)))
        name = forms.TextField(validator=MaxLength(40))
        description = forms.TextArea(cols=30, rows=3)


