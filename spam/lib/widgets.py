from tg import config, url
from tg import app_globals as G
from tw.api import Widget, WidgetsList, JSLink
from tw.forms import TableForm, TextField, TextArea, HiddenField
from tw.forms import CalendarDatePicker
from tw.forms.validators import All, Regex, MaxLength, NotEmpty, Int
from spam.lib.twlib.livetable import LiveTable, IconButton, TextData

# Orbited
orbited_address = config.get('orbited_address', 'http://localhost:9000')

orbited_js = JSLink(link='%s/static/Orbited.js' % orbited_address)
initsocket_js = JSLink(link=url('/js/init_TCPSocket.js'))
stomp_js = JSLink(link='%s/static/protocols/stomp/stomp.js' % orbited_address)

# JQuery and plugins
jquery_js = JSLink(link=url('/js/jquery.js'))
jquery_ui_js = JSLink(link=url('/js/jquery-ui.js'))
jquery_tools_js = JSLink(link=url('/js/jquery.tools.js'))
jquery_cookie_js = JSLink(link=url('/js/jquery.cookie.js'))
jquery_treeview_js = JSLink(link=url('/js/jquery.treeview.js'))
jquery_sprintf_js = JSLink(link=url('/js/jquery.sprintf.js'))
jquery_tablesorter_js = JSLink(link=url('/js/jquery.tablesorter.js'))

# SPAM
spam_js = JSLink(link=url('/parsedjs/spam.js'))
spam_stomp_client_js = JSLink(link=url('/parsedjs/spam_stomp_client.js'))


class NetworkingJS(Widget):
    javascript = [orbited_js, initsocket_js, stomp_js]

class StartupJS(Widget):
    javascript = [jquery_js, jquery_ui_js, jquery_tools_js, jquery_cookie_js,
                  jquery_treeview_js, jquery_sprintf_js, jquery_tablesorter_js,
                  spam_js]

# Custom LiveTable widgets
class SchemaButton(IconButton):
    template = 'mako:spam.templates.widgets.schema_button'

# Live tables
class ProjectsActive(LiveTable):
    javascript = [spam_stomp_client_js]
    update_topic = '/topic/projects'
    update_condition = '!data.ob.archived || data.update_type=="archived"'
    update_functions = ('{"added": livetable.addrow,'
                        ' "deleted": livetable.deleterow,'
                        ' "updated": livetable.updaterow,'
                        ' "archived": livetable.deleterow,'
                        ' "activated": livetable.addrow}')

    class fields(WidgetsList):
        archive = IconButton(icon_class='archive', action='%(id)s/archive')
        edit = IconButton(icon_class='edit', action='%(id)s/edit')
        delete = IconButton(icon_class='delete', action='%(id)s/delete')
        schema = SchemaButton(action={'uptodate': '',
                                      'outdated': '%(id)s/upgrade'})
        id = TextData()
        name = TextData()
        description = TextData()
        created = TextData(sort_default=True)


class ProjectsArchived(LiveTable):
    javascript = [spam_stomp_client_js]
    update_topic = '/topic/projects'
    update_condition = 'data.ob.archived || data.update_type=="activated"'
    update_functions = ('{"added": livetable.addrow,'
                        ' "deleted": livetable.deleterow,'
                        ' "updated": livetable.updaterow,'
                        ' "archived": livetable.addrow,'
                        ' "activated": livetable.deleterow}')

    class fields(WidgetsList):
        reactivate = IconButton(icon_class='activate', action='%(id)s/activate')
        id = TextData()
        name = TextData()
        description = TextData()
        created = TextData(sort_default=True)


# Form widgets

# Project
class FormProjectNew(TableForm):
    class fields(WidgetsList):
        proj = TextField(label_text='id', validator=All(Regex(G.pattern_name,
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


# Scene
class FormSceneNew(TableForm):
    class fields(WidgetsList):
        proj = HiddenField(validator=NotEmpty)
        _project = TextField(validator=None, disabled=True)
        sc = TextField(label_text='name', validator=All(Regex(G.pattern_name,
                                                not_empty=True), MaxLength(15)))
        description = TextArea(cols=30, rows=3)


class FormSceneEdit(TableForm):
    class fields(WidgetsList):
        _method = HiddenField(default='PUT', validator=None)
        proj = HiddenField(validator=NotEmpty)
        sc = HiddenField(validator=NotEmpty)
        _project = TextField(validator=None, disabled=True)
        _name = TextField(validator=None, disabled=True)
        description = TextArea(cols=30, rows=3)


class FormSceneConfirm(TableForm):
    class fields(WidgetsList):
        _method = HiddenField(default='', validator=None)
        proj = HiddenField(validator=NotEmpty)
        sc = HiddenField(validator=NotEmpty)
        _project = TextField(validator=None, disabled=True)
        _name = TextField(validator=None, disabled=True)
        _description = TextArea(cols=30, rows=3, disabled=True, validator=None)


# Shot
class FormShotNew(TableForm):
    class fields(WidgetsList):
        proj = HiddenField(validator=NotEmpty)
        sc = HiddenField(validator=NotEmpty)
        _project = TextField(validator=None, disabled=True)
        _scene = TextField(validator=None, disabled=True)
        sh = TextField(label_text='name', validator=All(Regex(G.pattern_name,
                                                not_empty=True), MaxLength(15)))
        description = TextArea(cols=30, rows=3)
        action = TextArea(cols=30, rows=3)
        frames = TextField(validator=Int)
        handle_in = TextField(validator=Int)
        handle_out = TextField(validator=Int)


class FormShotEdit(TableForm):
    class fields(WidgetsList):
        _method = HiddenField(default='PUT', validator=None)
        proj = HiddenField(validator=NotEmpty)
        sc = HiddenField(validator=NotEmpty)
        sh = HiddenField(validator=NotEmpty)
        _project = TextField(validator=None, disabled=True)
        _scene = TextField(validator=None, disabled=True)
        _name = TextField(validator=None, disabled=True)
        description = TextArea(cols=30, rows=3)
        action = TextArea(cols=30, rows=3)
        frames = TextField(validator=Int)
        handle_in = TextField(validator=Int)
        handle_out = TextField(validator=Int)


class FormShotConfirm(TableForm):
    class fields(WidgetsList):
        _method = HiddenField(default='', validator=None)
        proj = HiddenField(validator=NotEmpty)
        sc = HiddenField(validator=NotEmpty)
        sh = HiddenField(validator=NotEmpty)
        _project = TextField(validator=None, disabled=True)
        _scene = TextField(validator=None, disabled=True)
        _name = TextField(validator=None, disabled=True)
        _description = TextArea(cols=30, rows=3, validator=None, disabled=True)
        _action = TextArea(cols=30, rows=3, validator=None, disabled=True)
        _frames = TextField(validator=None, disabled=True)
        _handle_in = TextField(validator=None, disabled=True)
        _handle_out = TextField(validator=None, disabled=True)



