import tg
from tw.api import Widget, WidgetsList, JSLink
from tw.forms import TableForm, TextField, TextArea, HiddenField
from tw.forms import CalendarDatePicker
from tw.forms.validators import All, Regex, MaxLength, NotEmpty
from spam.lib.repo import pattern_nick
from spam.lib.twlib.livetable import LiveTable, IconButton, TextData

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
class ProjectsActive(LiveTable):
    class fields(WidgetsList):
        edit = IconButton(icon_class='edit', action='edit')
        archive = IconButton(icon_class='archive')
        delete = IconButton(icon_class='delete', action='delete')
        id = TextData()
        name = TextData()
        description = TextData()
        created = TextData()


class ProjectsArchived(LiveTable):
    class fields(WidgetsList):
        reactivate = IconButton(icon_class='activate')
        id = TextData()
        name = TextData()
        description = TextData()
        created = TextData()


# Form widgets
class FormProjectNew(TableForm):
    class fields(WidgetsList):
        proj = TextField(label_text='id', validator=All(Regex(pattern_nick,
                                                not_empty=True), MaxLength(15)))
        name = TextField(validator=MaxLength(40))
        description = TextArea(cols=30, rows=3)


class FormProjectEdit(TableForm):
    class fields(WidgetsList):
        _method = HiddenField(default='PUT', validator=None)
        proj = HiddenField(validator=NotEmpty)
        proj_d = TextField(label_text='id', disabled=True, validator=None)
        name = TextField(validator=MaxLength(40))
        description = TextArea(cols=30, rows=3)


class FormProjectDelete(TableForm):
    class fields(WidgetsList):
        _method = HiddenField(default='DELETE', validator=None)
        proj = HiddenField(validator=NotEmpty)
        proj_d = TextField(label_text='id', disabled=True, validator=None)
        name_d = TextField(label_text='name', disabled=True, validator=None)
        description_d = TextArea(label_text='description', cols=30, rows=3,
                                                disabled=True, validator=None)
        create_d = CalendarDatePicker(label_text='created',
                                                disabled=True, validator=None)
    submit_text = 'delete'
