from tg import config, url
from tg import app_globals as G
from pylons.i18n import ugettext as _, lazy_ugettext as l_
from tw.api import Widget, WidgetsList, JSLink, js_function
from tw.forms import TableForm, TextField, TextArea, HiddenField, FormField
from tw.forms import CalendarDatePicker, SingleSelectField, FileField, Spacer
from tw.forms import PasswordField, MultipleSelectField
from tw.forms.validators import All, Any, Regex, MaxLength, NotEmpty, Int
from tw.forms.validators import Schema
from spam.lib.validators import CategoryNamingConvention
from livewidgets import LiveTable, LiveBox, LiveList
from livewidgets import LiveWidget, Box, IconButton, IconLink, Text, Link, Thumb
from spam.lib.notifications import TOPIC_JOURNAL

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

############################################################
# Custom Live widgets
############################################################
class StatusIcon(LiveWidget):
    params = ['icon_class']
    template = 'mako:spam.templates.widgets.statusicon'
    
    field_class = 'statusicon'
    show_header = False
    sortable = False


class StatusIconBox(LiveWidget):
    params = ['icon_class']
    template = 'mako:spam.templates.widgets.statusiconbox'
    
    field_class = 'statusiconbox'
    show_header = False
    sortable = False


############################################################
# Live tables
############################################################
class TableTest(LiveTable):
    show_headers = True
    class fields(WidgetsList):
        a = Text(sort_default=True, sort_direction='desc')
        b = Link()
        thumb = Thumb(label_text='preview',
            src=url('/repo/%(proj_id)s/%(name)s/thumb.png'),
            dest=url('/repo/%(proj_id)s/%(name)s/preview.png')
        )
        actions = Box(fields=[
            IconButton(id='edit', icon_class='edit',
              action=url('/user/%(user_name)s/edit')),
            IconButton(id='delete', icon_class='delete',
              action=url('/user/%(user_name)s/delete')),
        ])


class TableUsers(LiveTable):
    javascript = [notify_client_js]
    update_topic = '/topic/users'
    class fields(WidgetsList):
        domain = Text()
        user_name = Text(sort_default=True)
        display_name = Text()
        actions = Box(fields=[
            IconButton(id='edit', icon_class='edit',
              label_text=_('edit'),
              action=url('/user/%(user_name)s/edit')),
            IconButton(id='delete', icon_class='delete',
              label_text=_('delete'),
              action=url('/user/%(user_name)s/delete')),
        ])


class TableGroupUsers(LiveTable):
    javascript = [notify_client_js]
    update_topic = '/topic/groups'
    class fields(WidgetsList):
        user_name = Text(sort_default=True)
        display_name = Text()
        actions = Box(fields=[
            IconButton(id='remove', icon_class='delete',
              label_text=_('remove'),
              action=url(
                    '/user/%(user_name)s/%(group_name)s/remove_from_group')),
        ])
    
    def update_params(self, d):
        super(TableGroupUsers, self).update_params(d)
        d['update_condition'] = 'msg.group_name=="%s"' % (
                                                d['extra_data']['group_name'])


class TableProjectAdmins(LiveTable):
    javascript = [notify_client_js]
    update_topic = '/topic/project_admins'
    class fields(WidgetsList):
        user_name = Text(sort_default=True)
        display_name = Text()
        actions = Box(fields=[
            IconButton(id='remove', icon_class='delete',
              label_text=_('remove'),
              action=url('/user/%(proj)s/%(user_name)s/remove_admin')),
        ])
    
    def update_params(self, d):
        super(TableProjectAdmins, self).update_params(d)
        d['update_condition'] = 'msg.proj=="%s"' % d['extra_data']['proj']


class TableProjectSupervisors(LiveTable):
    javascript = [notify_client_js]
    update_topic = '/topic/project_supervisors'
    class fields(WidgetsList):
        user_name = Text(sort_default=True)
        display_name = Text()
        actions = Box(fields=[
            IconButton(id='remove', icon_class='delete',
              label_text=_('remove'),
              action=url(
                    '/user/%(proj)s/%(cat)s/%(user_name)s/remove_supervisor')),
        ])
    
    def update_params(self, d):
        super(TableProjectSupervisors, self).update_params(d)
        d['update_condition'] = 'msg.proj=="%s" && msg.cat=="%s"' % (
                            (d['extra_data']['proj'], d['extra_data']['cat']))


class TableProjectArtists(LiveTable):
    javascript = [notify_client_js]
    update_topic = '/topic/project_artists'
    class fields(WidgetsList):
        user_name = Text(sort_default=True)
        display_name = Text()
        actions = Box(fields=[
            IconButton(id='remove', icon_class='delete',
              label_text=_('remove'),
              action=url('/user/%(proj)s/%(cat)s/%(user_name)s/remove_artist')),
        ])
    
    def update_params(self, d):
        super(TableProjectArtists, self).update_params(d)
        d['update_condition'] = 'msg.proj=="%s" && msg.cat=="%s"' % (
                            (d['extra_data']['proj'], d['extra_data']['cat']))


class TableCategories(LiveTable):
    javascript = [notify_client_js]
    update_topic = '/topic/categories'
    class fields(WidgetsList):
        ordering = Text(sort_default=True)
        id = Text()
        naming_convention = Text()
        actions = Box(fields=[
            IconButton(id='edit', icon_class='edit',
              label_text=_('edit'),
              action=url('/category/%(id)s/edit')),
            IconButton(id='delete', icon_class='delete',
              label_text=_('delete'),
              action=url('/category/%(id)s/delete')),
        ])


class ProjectsActive(LiveTable):
    javascript = [notify_client_js]
    update_topic = '/topic/projects'
    update_condition = '!msg.ob.archived || msg.update_type=="archived"'
    update_functions = ('{"added": lw.livetable.addrow,'
                        ' "deleted": lw.livetable.deleterow,'
                        ' "updated": lw.livetable.updaterow,'
                        ' "archived": lw.livetable.deleterow,'
                        ' "activated": lw.livetable.addrow}')

    class fields(WidgetsList):
        id = Text()
        name = Text()
        description = Text()
        actions = Box(fields=[
            IconButton(id='archive', icon_class='archive',
              label_text=_('archive'),
              action='%(id)s/archive'),
            IconButton(id='edit', icon_class='edit',
              label_text=_('edit'),
              action='%(id)s/edit'),
            IconButton(id='delete', icon_class='delete',
              label_text=_('delete'),
              action='%(id)s/delete'),
        ])


class ProjectsArchived(LiveTable):
    javascript = [notify_client_js]
    update_topic = '/topic/projects'
    update_condition = 'msg.ob.archived || msg.update_type=="activated"'
    update_functions = ('{"added": lw.livetable.addrow,'
                        ' "deleted": lw.livetable.deleterow,'
                        ' "updated": lw.livetable.updaterow,'
                        ' "archived": lw.livetable.addrow,'
                        ' "activated": lw.livetable.deleterow}')

    class fields(WidgetsList):
        id = Text()
        name = Text()
        description = Text()
        actions = Box(fields=[
            IconButton(id='activate', icon_class='activate',
              label_text=_('activate'),
              action='%(id)s/activate'),
        ])


class TableScenes(LiveTable):
    javascript = [notify_client_js]
    update_topic = '/topic/scenes'
    class fields(WidgetsList):
        thumbnail = Thumb(label_text='preview', field_class='thumbnail',
            src=url('/repo/%(proj_id)s/%(name)s/thumb.png'),
            dest=url('/repo/%(proj_id)s/%(name)s/preview.png')
        )
        name = Link(dest=url('/scene/%(proj_id)s/%(name)s/'),
                        sort_default=True)
        description = Text()
        shots = StatusIconBox(fields=[
            StatusIcon(label_text='')
        ])
        actions = Box(fields=[
            IconButton(id='edit', icon_class='edit',
              label_text=_('edit'),
              action=url('/scene/%(proj_id)s/%(name)s/edit')),
            IconButton(id='delete', icon_class='delete',
              label_text=_('delete'),
              action=url('/scene/%(proj_id)s/%(name)s/delete')),
        ])


class TableShots(LiveTable):
    javascript = [notify_client_js]
    update_topic = '/topic/shots'
    class fields(WidgetsList):
        thumbnail = Thumb(label_text='preview', field_class='thumbnail',
            src=url('/repo/%(proj_id)s/%(parent_name)s/%(name)s/thumb.png'),
            dest=url('/repo/%(proj_id)s/%(parent_name)s/%(name)s/preview.png')
        )
        name = Link(dest=url('/shot/%(proj_id)s/%(parent_name)s/%(name)s/'),
                        sort_default=True)
        description = Text()
        frames = Text()
        categories = StatusIconBox(fields=[
            StatusIcon(label_text='')
        ])
        actions = Box(fields=[
            IconButton(id='edit', icon_class='edit',
              label_text=_('edit'),
              action=url('/shot/%(proj_id)s/%(parent_name)s/%(name)s/edit')),
            IconButton(id='delete', icon_class='delete',
              label_text=_('delete'),
              action=url('/shot/%(proj_id)s/%(parent_name)s/%(name)s/delete')),
        ])


class TableLibgroups(LiveTable):
    javascript = [notify_client_js]
    update_topic = '/topic/libgroups'
    class fields(WidgetsList):
        thumbnail = Thumb(label_text='preview', field_class='thumbnail',
            src=url('/repo/%(proj_id)s/%(id)s/thumb.png'),
            dest=url('/repo/%(proj_id)s/%(id)s/preview.png')
        )
        name = Link(dest=url('/libgroup/%(proj_id)s/%(id)s/'),
                        sort_default=True)
        description = Text()
        subgroups = StatusIconBox(fields=[
            StatusIcon(label_text='')
        ])
        categories = StatusIconBox(fields=[
            StatusIcon(label_text='')
        ])
        actions = Box(fields=[
            IconButton(id='edit', icon_class='edit',
              label_text=_('edit'),
              action=url('/libgroup/%(proj_id)s/%(id)s/edit')),
            IconButton(id='delete', icon_class='delete',
              label_text=_('delete'),
              action=url('/libgroup/%(proj_id)s/%(id)s/delete')),
        ])


class TableAssets(LiveTable):
    params = ['category']
    
    javascript = [notify_client_js]
    update_topic = '/topic/assets'
    class fields(WidgetsList):
        thumbnail = Thumb(label_text='preview', field_class='thumbnail',
            src=url('/repo/%(thumb_path)s'),
            dest=url('/repo/%(proj_id)s/preview.png')
        )
        name = Text(sort_default=True)
        current_fmtver = Text(label_text=_('version'))
        status = StatusIcon(icon_class='asset', label_text=_('status: '))
        note = Box(fields=[
            Text(id='current_header', field_class='note_header',
              label_text=_('latest comment')),
            Text(id='current_summary', label_text=_('latest comment')),
        ])
        actions = Box(fields=[
            IconButton(id='history', icon_class='history',
              label_text=_('asset history'),
              action=url('/asset/%(proj_id)s/%(id)s')),
            IconButton(id='addnote', icon_class='edit',
              label_text=_('add note'),
              action=url('/note/%(current_id)s/new')),
            IconButton(id='checkout', icon_class='checkout',
              label_text=_('checkout'),
              action=url('/asset/%(proj_id)s/%(id)s/checkout'),
              condition='!data.checkedout && !data.approved'),
            IconButton(id='release', icon_class='release',
              label_text=_('release'),
              action=url('/asset/%(proj_id)s/%(id)s/release'),
              condition='data.checkedout && !data.submitted && !data.approved'),
            IconButton(id='publish', icon_class='publish',
              label_text=_('publish a new version'),
              action=url('/asset/%(proj_id)s/%(id)s/publish'),
              condition='data.checkedout'),
            IconButton(id='submit', icon_class='submit',
              label_text=_('submit for approval'),
              action=url('/asset/%(proj_id)s/%(id)s/submit'),
              condition='data.checkedout && data.current_ver>0 '
                        '&& !data.submitted && !data.approved'),
            IconButton(id='recall', icon_class='recall',
              label_text=_('recall submission'),
              action=url('/asset/%(proj_id)s/%(id)s/recall'),
              condition='data.submitted && !(data.approved)'),
            IconButton(id='sendback', icon_class='sendback',
              label_text=_('send back for revisions'),
              action=url('/asset/%(proj_id)s/%(id)s/sendback'),
              condition='data.submitted && !(data.approved)'),
            IconButton(id='approve', icon_class='approve',
              label_text=_('approve'),
              action=url('/asset/%(proj_id)s/%(id)s/approve'),
              condition='data.submitted && !(data.approved)'),
            IconButton(id='revoke', icon_class='revoke',
              label_text=_('revoke approval'),
              action=url('/asset/%(proj_id)s/%(id)s/revoke'),
              condition='data.approved'),
            IconButton(id='delete', icon_class='delete',
              label_text=_('delete'),
              action=url('/asset/%(proj_id)s/%(id)s/delete')),
        ])
    
    def update_params(self, d):
        super(TableAssets, self).update_params(d)
        d['update_condition'] = 'msg.ob.category.id=="%s"' % d['category']


class TableAssetHistory(LiveTable):
    class fields(WidgetsList):
        thumbnail = Box(fields=[
          Thumb(id='preview', label_text=_('preview'), field_class='thumbnail',
            condition='data.thumb_path',
            src=url('/repo/%(thumb_path)s'),
            dest=url('/repo/%(thumb_path)s')
          )
        ])
        fmtver = Text(label_text='ver')
        note = Box(fields=[
            Text(id='header', field_class='note_header',
              label_text=''),
            Box(id='lines', fields=[Text(id='text', label_text='')]),
        ])
        actions = Box(fields=[
            IconLink(id='download', icon_class='download',
              condition='data.ver && data.ver>0',
              label_text=_('download'),
              dest=url('/asset/%(proj_id)s/%(id)s/download')),
        ])


class TableJournal(LiveTable):
    params = ['curpage']
    javascript = [notify_client_js]
    update_topic = TOPIC_JOURNAL
    class fields(WidgetsList):
        strftime = Text(label_text='date', sort_default=True,
                                                        sort_direction = 'desc')
        user_id = Text(label_text='user')
        text = Text()
    
    def update_params(self, d):
        super(TableJournal, self).update_params(d)
        d['update_condition'] = '%s==1' % d['curpage']


############################################################
# Live lists
############################################################
class ListTags(LiveList):
    class fields(WidgetsList):
        id = Text()


class ListNotes(LiveList):
    class fields(WidgetsList):
        text = Text()


############################################################
# Live boxes
############################################################
class BoxStatus(LiveBox):
    container_class = 'statusbox'
    
    class fields(WidgetsList):
        status = StatusIcon(label_text='')


############################################################
# Form widgets
############################################################

# User
class FormUserNew(TableForm):
    class fields(WidgetsList):
        user_name = TextField(validator=MaxLength(16, not_empty=True))
        display_name = TextField(validator=MaxLength(255, not_empty=True))
        password = PasswordField(validator=MaxLength(80, not_empty=True))


class FormUserEdit(TableForm):
    class fields(WidgetsList):
        _method = HiddenField(default='PUT', validator=None)
        user_id = HiddenField(validator=NotEmpty)
        user_name_ = TextField(disabled=True, validator=None)
        display_name = TextField(validator=MaxLength(255, not_empty=True))


class FormUserConfirm(TableForm):
    class fields(WidgetsList):
        _method = HiddenField(default='', validator=None)
        user_id = HiddenField(validator=NotEmpty)
        user_name_ = TextField(disabled=True, validator=None)
        display_name_ = TextField(disabled=True, validator=None)


class FormUserAddToGroup(TableForm):
    class fields(WidgetsList):
        _method = HiddenField(default='ADD_TO_GROUP', validator=None)
        group_id = HiddenField(validator=NotEmpty)
        userids = MultipleSelectField(label_text='Users', options=[], size=20)


class FormUserAddAdmins(TableForm):
    class fields(WidgetsList):
        _method = HiddenField(default='ADD_ADMINS', validator=None)
        proj = HiddenField(validator=NotEmpty)
        userids = MultipleSelectField(label_text='Users', options=[], size=20)


class FormUserAddToCategory(TableForm):
    class fields(WidgetsList):
        _method = HiddenField(default='', validator=None)
        proj = HiddenField(validator=NotEmpty)
        category_id = HiddenField(validator=NotEmpty)
        userids = MultipleSelectField(label_text='Users', options=[], size=20)


# Category
class FormCategoryNew(TableForm):
    class fields(WidgetsList):
        category_id = TextField(validator=All(
                          Regex(G.pattern_name, not_empty=True), MaxLength(30)))
        ordering = TextField(validator=Int)
        naming_convention = TextField(validator=MaxLength(255))

class FormCategoryEdit(TableForm):
    class fields(WidgetsList):
        _method = HiddenField(default='PUT', validator=None)
        category_id = HiddenField(validator=NotEmpty)
        id_ = TextField(disabled=True, validator=None)
        ordering = TextField(validator=Int)
        naming_convention = TextField(validator=MaxLength(255))


class FormCategoryConfirm(TableForm):
    class fields(WidgetsList):
        _method = HiddenField(default='', validator=None)
        category_id = HiddenField(validator=NotEmpty)
        id_ = TextField(disabled=True, validator=None)
        ordering_ = TextField(disabled=True, validator=None)
        naming_convention_ = TextField(disabled=True, validator=None)


# Tags
class FormTagNew(TableForm):
    class fields(WidgetsList):
        taggable_id = HiddenField(validator=NotEmpty)
        current_tags_ = TextField(validator=None, disabled=True)
        tag_ids = MultipleSelectField(label_text='Tags', options=[], size=10)
        new_tags = TextField(validator=Regex(G.pattern_tags))


class FormTagConfirm(TableForm):
    class fields(WidgetsList):
        _method = HiddenField(default='', validator=None)
        tag_id = HiddenField(validator=NotEmpty)


class FormTagRemove(TableForm):
    class fields(WidgetsList):
        _method = HiddenField(default='REMOVE', validator=None)
        taggable_id = HiddenField(validator=NotEmpty)
        tag_ids = MultipleSelectField(label_text='Tags', options=[], size=10)


# Notes
class FormNoteNew(TableForm):
    class fields(WidgetsList):
        annotable_id = HiddenField(validator=NotEmpty)
        text = TextArea(cols=30, rows=3)
        

class FormNoteConfirm(TableForm):
    class fields(WidgetsList):
        _method = HiddenField(default='', validator=None)
        note_id = HiddenField(validator=NotEmpty)
        text_ = TextArea(cols=30, rows=3, disabled=True, validator=None)


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


class FormShotAddTag(TableForm):
    class fields(WidgetsList):
        _method = HiddenField(default='ADD_TAG', validator=None)
        proj = HiddenField(validator=NotEmpty)
        sc = HiddenField(validator=NotEmpty)
        sh = HiddenField(validator=NotEmpty)
        current_tags_ = TextField(validator=None, disabled=True)
        tag_ids = MultipleSelectField(label_text='Tags', options=[], size=10)
        new_tags = TextField(validator=Regex(G.pattern_tags))


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
                validator=All(Regex(G.pattern_name, not_empty=True),
                                                                MaxLength(30)),
                default='')
        comment = TextArea(cols=30, rows=3)
    
    validator = Schema(
        chained_validators=[CategoryNamingConvention('category_id', 'name')],
        )

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


class FormAssetStatus(TableForm):
    class fields(WidgetsList):
        _method = HiddenField(default='', validator=None)
        proj = HiddenField(validator=NotEmpty)
        project_ = TextField(validator=None, disabled=True)
        asset_id = HiddenField(validator=NotEmpty)
        container_ = TextField(validator=None, disabled=True)
        category_ = TextField(validator=None, disabled=True)
        name_ = TextField(validator=None, disabled=True)
        comment = TextArea(cols=30, rows=3)

