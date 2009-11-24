from tg import config, url
from tw.api import Widget, WidgetsList, JSLink
from tw.forms import TableForm, TextField, TextArea, HiddenField
from tw.forms import CalendarDatePicker
from tw.forms.validators import All, Regex, MaxLength, NotEmpty
from spam.lib.repo import pattern_proj
from spam.lib.twlib.livetable import LiveTable, IconButton, TextData

# Orbited
orbited_address = config.get('orbited_address', 'http://localhost:9000')

orbited_js = JSLink(link='%s/static/Orbited.js' % orbited_address)
initsocket_js = JSLink(link=url('/js/init_TCPSocket.js'))
stomp_js = JSLink(link='%s/static/protocols/stomp/stomp.js' % orbited_address)

# SPAM
spam_js = JSLink(link=url('/parsedjs/spam.js'))

# JQuery and plugins
jquery_js = JSLink(link=url('/js/jquery.js'))
overlay_js = JSLink(link=url('/js/tools.overlay.js'))
jquery_cookie_js = JSLink(link=url('/js/jquery.cookie.js'))
jquery_treeview_js = JSLink(link=url('/js/jquery.treeview.js'))
jquery_sprintf_js = JSLink(link=url('/js/jquery.sprintf.js'))


class NetworkingJS(Widget):
    javascript = [orbited_js, initsocket_js, stomp_js]

class StartupJS(Widget):
    javascript = [jquery_js, spam_js, overlay_js, jquery_cookie_js,
                  jquery_treeview_js, jquery_sprintf_js]

# Custom LiveTable widgets
class SchemaButton(IconButton):
    template = 'mako:spam.templates.widgets.schema_button'

# Live tables
class ProjectsActive(LiveTable):
    update_topic = '/topic/project'
    update_condition = '!data.project.archived'

    class fields(WidgetsList):
        archive = IconButton(icon_class='archive', action='%(id)s/archive')
        edit = IconButton(icon_class='edit', action='%(id)s/edit')
        delete = IconButton(icon_class='delete', action='%(id)s/delete')
        schema = SchemaButton(action={'uptodate': '', 'outdated': '%(id)s/upgrade'})
        id = TextData()
        name = TextData()
        description = TextData()
        created = TextData()


class ProjectsArchived(LiveTable):
    update_topic = '/topic/project'
    update_condition = 'data.project.archived'

    class fields(WidgetsList):
        reactivate = IconButton(icon_class='activate', action='%(id)s/activate')
        id = TextData()
        name = TextData()
        description = TextData()
        created = TextData()


# Form widgets
class FormProjectNew(TableForm):
    class fields(WidgetsList):
        proj = TextField(label_text='id', validator=All(Regex(pattern_proj,
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


class FormProjectConfirm(TableForm):
    class fields(WidgetsList):
        _method = HiddenField(default='', validator=None)
        proj = HiddenField(validator=NotEmpty)
        proj_d = TextField(label_text='id', disabled=True, validator=None)
        name_d = TextField(label_text='name', disabled=True, validator=None)
        description_d = TextArea(label_text='description', cols=30, rows=3,
                                                disabled=True, validator=None)
        create_d = CalendarDatePicker(label_text='created',
                                                disabled=True, validator=None)


