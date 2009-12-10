from tg import config, url
from tg import app_globals as G
from tw.api import Widget, WidgetsList, JSLink, js_function
from tw.forms import TableForm, TextField, TextArea, HiddenField, FormField
from tw.forms import CalendarDatePicker, SingleSelectField, FileField, Spacer
from tw.forms.validators import All, Any, Regex, MaxLength, NotEmpty, Int
from spam.lib.twlib.livetable import LiveTable, IconButton, TextData, ThumbData
from spam.lib.twlib.livetable import IconBox, LinkData

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
notify_client_js = JSLink(link=url('/parsedjs/notify_client.js'))

# load LiveTable js on every page, so we can use it in tabs
livetable_js = JSLink(modname='spam.lib.twlib.livetable',
                      filename='static/livetable.js')

class NetworkingJS(Widget):
    javascript = [orbited_js, initsocket_js, stomp_js]


class NotifyClientJS(Widget):
    javascript = [notify_client_js]


class StartupJS(Widget):
    javascript = [jquery_js, jquery_ui_js, jquery_tools_js, jquery_cookie_js,
                  jquery_treeview_js, jquery_sprintf_js, jquery_tablesorter_js,
                  spam_js]

# Custom LiveTable widgets
class SchemaButton(IconButton):
    template = 'mako:spam.templates.widgets.schema_button'

# Live tables
class TableCategories(LiveTable):
    javascript = [notify_client_js]
    update_topic = '/topic/categories'
    class fields(WidgetsList):
        ordering = TextData(sort_default=True)
        name = TextData()
        actions = IconBox(buttons=[
            IconButton(id='edit', icon_class='edit',
              action=url('/category/%(name)s/edit')),
            IconButton(id='delete', icon_class='delete',
              action=url('/category/%(name)s/delete')),
        ])


class ProjectsActive(LiveTable):
    javascript = [notify_client_js]
    update_topic = '/topic/projects'
    update_condition = '!msg.ob.archived || msg.update_type=="archived"'
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
    javascript = [notify_client_js]
    update_topic = '/topic/projects'
    update_condition = 'msg.ob.archived || msg.update_type=="activated"'
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


class TableScenes(LiveTable):
    javascript = [notify_client_js]
    update_topic = '/topic/scenes'
    class fields(WidgetsList):
        thumbnail = ThumbData(label_text='preview',
            src=url('/repo/%(proj_id)s/%(name)s/thumb.png'),
            dest=url('/repo/%(proj_id)s/%(name)s/preview.png')
        )
        name = LinkData(dest=url('/scene/%(proj_id)s/%(name)s/'),
                        sort_default=True)
        description = TextData()
        actions = IconBox(buttons=[
            IconButton(id='edit', icon_class='edit',
              action=url('/scene/%(proj_id)s/%(name)s/edit')),
            IconButton(id='delete', icon_class='delete',
              action=url('/scene/%(proj_id)s/%(name)s/delete')),
        ])


class TableShots(LiveTable):
    javascript = [notify_client_js]
    update_topic = '/topic/shots'
    class fields(WidgetsList):
        thumbnail = ThumbData(label_text='preview',
            src=url('/repo/%(proj_id)s/%(parent_name)s/%(name)s/thumb.png'),
            dest=url('/repo/%(proj_id)s/%(parent_name)s/%(name)s/preview.png')
        )
        name = LinkData(dest=url('/shot/%(proj_id)s/%(parent_name)s/%(name)s/'),
                        sort_default=True)
        description = TextData()
        frames = TextData()
        actions = IconBox(buttons=[
            IconButton(id='edit', icon_class='edit',
              action=url('/shot/%(proj_id)s/%(parent_name)s/%(name)s/edit')),
            IconButton(id='delete', icon_class='delete',
              action=url('/shot/%(proj_id)s/%(parent_name)s/%(name)s/delete')),
        ])


class TableLibgroups(LiveTable):
    javascript = [notify_client_js]
    update_topic = '/topic/libgroups'
    class fields(WidgetsList):
        thumbnail = ThumbData(label_text='preview',
            src=url('/repo/%(proj_id)s/%(id)s/thumb.png'),
            dest=url('/repo/%(proj_id)s/%(id)s/preview.png')
        )
        name = LinkData(dest=url('/libgroup/%(proj_id)s/%(id)s/'),
                        sort_default=True)
        description = TextData()
        actions = IconBox(buttons=[
            IconButton(id='edit', icon_class='edit',
              action=url('/libgroup/%(proj_id)s/%(id)s/edit')),
            IconButton(id='delete', icon_class='delete',
              action=url('/libgroup/%(proj_id)s/%(id)s/delete')),
        ])


class TableAssets(LiveTable):
    params = ['category']
    
    javascript = [notify_client_js]
    update_topic = '/topic/assets'
    class fields(WidgetsList):
        thumbnail = ThumbData(label_text='preview',
            src=url('/repo/%(proj_id)s/thumb.png'),
            dest=url('/repo/%(proj_id)s/preview.png')
        )
        name = TextData(sort_default=True)
        current_fmtver = TextData(label_text='ver')
        actions = IconBox(buttons=[
            IconButton(id='checkout', icon_class='checkout',
              action=url('/asset/%(proj_id)s/%(id)s/checkout'),
              condition='!data.checkedout'),
            IconButton(id='release', icon_class='release',
              action=url('/asset/%(proj_id)s/%(id)s/release'),
              condition='data.checkedout'),
            IconButton(id='publish', icon_class='publish',
              action=url('/asset/%(proj_id)s/%(id)s/publish'),
              condition='data.checkedout'),
            IconButton(id='delete', icon_class='delete',
              action=url('/asset/%(proj_id)s/%(id)s/delete')),
        ])
    
    def update_params(self, d):
        super(TableAssets, self).update_params(d)
        d['update_condition'] = 'msg.ob.category.name=="%s"' % d['category']


class TableAssetHistory(LiveTable):
    class fields(WidgetsList):
        thumbnail = ThumbData(label_text='preview',
            src=url('/repo/%(proj_id)s/thumb.png'),
            dest=url('/repo/%(proj_id)s/preview.png')
        )
        fmtver = TextData(label_text='ver')


# Form widgets

# Category
class FormCategoryNew(TableForm):
    class fields(WidgetsList):
        name = TextField(validator=All(Regex(G.pattern_name, not_empty=True),
                                       MaxLength(30)))


class FormCategoryEdit(TableForm):
    class fields(WidgetsList):
        _method = HiddenField(default='PUT', validator=None)
        category_id = HiddenField(validator=All(NotEmpty, Int))
        name = TextField(validator=All(Regex(G.pattern_name, not_empty=True),
                                       MaxLength(30)))


class FormCategoryConfirm(TableForm):
    class fields(WidgetsList):
        _method = HiddenField(default='', validator=None)
        category_id = HiddenField(validator=All(NotEmpty, Int))
        name_ = TextField(disabled=True, validator=None)


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
        id_ = TextField(disabled=True, validator=None)
        name = TextField(validator=MaxLength(40))
        description = TextArea(cols=30, rows=3)


class FormProjectConfirm(TableForm):
    class fields(WidgetsList):
        _method = HiddenField(default='', validator=None)
        proj = HiddenField(validator=NotEmpty)
        id_ = TextField(disabled=True, validator=None)
        name_ = TextField(disabled=True, validator=None)
        description_ = TextArea(cols=30, rows=3, disabled=True, validator=None)
        created_ = CalendarDatePicker(disabled=True, validator=None)


# Scene
class FormSceneNew(TableForm):
    class fields(WidgetsList):
        proj = HiddenField(validator=NotEmpty)
        project_ = TextField(validator=None, disabled=True)
        sc = TextField(label_text='name', validator=All(Regex(G.pattern_name,
                                                not_empty=True), MaxLength(15)))
        description = TextArea(cols=30, rows=3)


class FormSceneEdit(TableForm):
    class fields(WidgetsList):
        _method = HiddenField(default='PUT', validator=None)
        proj = HiddenField(validator=NotEmpty)
        sc = HiddenField(validator=NotEmpty)
        project_ = TextField(validator=None, disabled=True)
        name_ = TextField(validator=None, disabled=True)
        description = TextArea(cols=30, rows=3)


class FormSceneConfirm(TableForm):
    class fields(WidgetsList):
        _method = HiddenField(default='', validator=None)
        proj = HiddenField(validator=NotEmpty)
        sc = HiddenField(validator=NotEmpty)
        project_ = TextField(validator=None, disabled=True)
        name_ = TextField(validator=None, disabled=True)
        description_ = TextArea(cols=30, rows=3, disabled=True, validator=None)


# Shot
class FormShotNew(TableForm):
    class fields(WidgetsList):
        proj = HiddenField(validator=NotEmpty)
        sc = HiddenField(validator=NotEmpty)
        project_ = TextField(validator=None, disabled=True)
        scene_ = TextField(validator=None, disabled=True)
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
        project_ = TextField(validator=None, disabled=True)
        scene_ = TextField(validator=None, disabled=True)
        name_ = TextField(validator=None, disabled=True)
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
        project_ = TextField(validator=None, disabled=True)
        scene_ = TextField(validator=None, disabled=True)
        name_ = TextField(validator=None, disabled=True)
        description_ = TextArea(cols=30, rows=3, validator=None, disabled=True)
        action_ = TextArea(cols=30, rows=3, validator=None, disabled=True)
        frames_ = TextField(validator=None, disabled=True)
        handle_in_ = TextField(validator=None, disabled=True)
        handle_out_ = TextField(validator=None, disabled=True)


# Libgroups
class FormLibgroupNew(TableForm):
    class fields(WidgetsList):
        proj = HiddenField(validator=NotEmpty)
        parent_id = HiddenField()
        project_ = TextField(validator=None, disabled=True)
        parent_ = TextField(validator=None, disabled=True)
        name = TextField(validator=All(Regex(G.pattern_name, not_empty=True),
                                       MaxLength(15)))
        description = TextArea(cols=30, rows=3)


class FormLibgroupEdit(TableForm):
    class fields(WidgetsList):
        _method = HiddenField(default='PUT', validator=None)
        proj = HiddenField(validator=NotEmpty)
        libgroup_id = HiddenField(validator=NotEmpty)
        project_ = TextField(validator=None, disabled=True)
        name_ = TextField(validator=None, disabled=True)
        description = TextArea(cols=30, rows=3)


class FormLibgroupConfirm(TableForm):
    class fields(WidgetsList):
        _method = HiddenField(default='', validator=None)
        proj = HiddenField(validator=NotEmpty)
        libgroup_id = HiddenField(validator=NotEmpty)
        project_ = TextField(validator=None, disabled=True)
        name_ = TextField(validator=None, disabled=True)
        description_ = TextArea(cols=30, rows=3, disabled=True, validator=None)


# Asset
class FormAssetNew(TableForm):
    class fields(WidgetsList):
        proj = HiddenField(validator=NotEmpty)
        container_type = HiddenField(validator=NotEmpty)
        container_id = HiddenField(validator=NotEmpty)
        project_ = TextField(validator=None, disabled=True)
        name = TextField(validator=Any(Regex(G.pattern_file, not_empty=True),
                                       Regex(G.pattern_seq, not_empty=True)))
        category_id = SingleSelectField(label_text='category', options=[],
                validator=Int(min=1,
                              messages={'tooLow': 'Please choose a category'}),
                default=0)

class FormAssetEdit(TableForm):
    class fields(WidgetsList):
        _method = HiddenField(default='PUT', validator=None)
        proj = HiddenField(validator=NotEmpty)
        project_ = TextField(validator=None, disabled=True)


class FormAssetConfirm(TableForm):
    class fields(WidgetsList):
        _method = HiddenField(default='', validator=None)
        proj = HiddenField(validator=NotEmpty)
        project_ = TextField(validator=None, disabled=True)
        asset_id = HiddenField(validator=NotEmpty)
        container_ = TextField(validator=None, disabled=True)
        category_ = TextField(validator=None, disabled=True)
        name_ = TextField(validator=None, disabled=True)


class Upload(FormField):
    template = 'mako:spam.templates.widgets.upload'
    upload_js = JSLink(link=url('/parsedjs/upload.js'))
    javascript = [upload_js]


class FormAssetPublish(TableForm):
    class fields(WidgetsList):
        _method = HiddenField(default='PUBLISH', validator=None)
        proj = HiddenField(validator=NotEmpty)
        asset_id = HiddenField(validator=NotEmpty)
        uploaded = HiddenField(validator=NotEmpty(
                    messages={'empty': 'Please choose the file(s) to upload'}))
        uploader = Upload(label_text='File(s) to Upload')
        spacer = Spacer(label_text='')
        comment = TextArea(cols=30, rows=3)

