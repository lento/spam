from tg import config, url
from tg import app_globals as G
from pylons.i18n import ugettext as _, lazy_ugettext as l_
from tw.api import Widget, WidgetsList, JSLink, JSSource, js_function
from tw.forms import TableForm, TextField, TextArea, HiddenField, FormField
from tw.forms import CalendarDatePicker, SingleSelectField, FileField, Spacer
from tw.forms import PasswordField, MultipleSelectField
from tw.forms.validators import All, Any, Regex, MaxLength, NotEmpty, Int
from tw.forms.validators import Schema
from spam.lib.validators import CategoryNamingConvention
from livewidgets import LiveTable, LiveBox, LiveList
from livewidgets import LiveWidget, Box, Button, Icon, Text, Link, Image
from spam.lib.notifications import notify

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
        actions = Box(fields=[
            Button(id='edit',
              action=url('/user/%(user_name)s/edit'),
              fields=[Icon(id='edit', icon_class='edit')]
            ),
            Button(id='delete', icon_class='delete',
              action=url('/user/%(user_name)s/delete'),
              fields=[Icon(id='delete', icon_class='delete')]
            ),
        ])


class TableUsers(LiveTable):
    javascript = [notify_client_js]
    update_topic = notify.TOPIC_USERS
    class fields(WidgetsList):
        domain = Text()
        user_name = Text(sort_default=True)
        display_name = Text()
        actions = Box(fields=[
            Button(id='edit',
              action=url('/user/%(user_name)s/edit'),
              fields=[Icon(id='edit', icon_class='edit',
                label_text=_('edit')),
            ]),
            Button(id='delete',
              action=url('/user/%(user_name)s/delete'),
              fields=[Icon(id='delete', icon_class='delete',
                label_text=_('delete')),
            ]),
        ])


class TableGroupUsers(LiveTable):
    javascript = [notify_client_js]
    update_topic = notify.TOPIC_GROUPS
    class fields(WidgetsList):
        user_name = Text(sort_default=True)
        display_name = Text()
        actions = Box(fields=[
            Button(id='remove',
              action=url(
                '/user/%(user_name)s/%(group_name)s/remove_from_group'),
              fields=[Icon(id='delete', icon_class='delete',
                label_text=_('remove')),
            ]),
        ])
    
    def update_params(self, d):
        super(TableGroupUsers, self).update_params(d)
        d['update_condition'] = 'msg.group_name=="%s"' % (
                                                d['extra_data']['group_name'])


class TableProjectAdmins(LiveTable):
    javascript = [notify_client_js]
    update_topic = notify.TOPIC_PROJECT_ADMINS
    class fields(WidgetsList):
        user_name = Text(sort_default=True)
        display_name = Text()
        actions = Box(fields=[
            Button(id='remove',
              action=url('/user/%(proj)s/%(user_name)s/remove_admin'),
              fields=[Icon(id='delete', icon_class='delete',
                label_text=_('remove')),
            ]),
        ])
    
    def update_params(self, d):
        super(TableProjectAdmins, self).update_params(d)
        d['update_condition'] = 'msg.proj=="%s"' % d['extra_data']['proj']


class TableProjectSupervisors(LiveTable):
    javascript = [notify_client_js]
    update_topic = notify.TOPIC_PROJECT_SUPERVISORS
    class fields(WidgetsList):
        user_name = Text(sort_default=True)
        display_name = Text()
        actions = Box(fields=[
            Button(id='remove',
              action=url(
                    '/user/%(proj)s/%(cat)s/%(user_name)s/remove_supervisor'),
              fields=[Icon(id='delete', icon_class='delete',
                label_text=_('remove')),
            ]),
        ])
    
    def update_params(self, d):
        super(TableProjectSupervisors, self).update_params(d)
        d['update_condition'] = 'msg.proj=="%s" && msg.cat=="%s"' % (
                            (d['extra_data']['proj'], d['extra_data']['cat']))


class TableProjectArtists(LiveTable):
    javascript = [notify_client_js]
    update_topic = notify.TOPIC_PROJECT_ARTISTS
    class fields(WidgetsList):
        user_name = Text(sort_default=True)
        display_name = Text()
        actions = Box(fields=[
            Button(id='remove', icon_class='delete',
              label_text=_('remove'),
              action=url('/user/%(proj)s/%(cat)s/%(user_name)s/remove_artist'),
              fields=[Icon(id='delete', icon_class='delete',
                label_text=_('remove')),
            ]),
        ])
    
    def update_params(self, d):
        super(TableProjectArtists, self).update_params(d)
        d['update_condition'] = 'msg.proj=="%s" && msg.cat=="%s"' % (
                            (d['extra_data']['proj'], d['extra_data']['cat']))


class TableCategories(LiveTable):
    javascript = [notify_client_js]
    update_topic = notify.TOPIC_CATEGORIES
    class fields(WidgetsList):
        ordering = Text(sort_default=True)
        id = Text()
        naming_convention = Text()
        actions = Box(fields=[
            Button(id='edit',
              action=url('/category/%(id)s/edit'),
              fields=[Icon(id='edit', icon_class='edit',
                label_text=_('edit')),
            ]),
            Button(id='delete',
              label_text=_('delete'),
              action=url('/category/%(id)s/delete'),
              fields=[Icon(id='delete', icon_class='delete',
                label_text=_('delete')),
            ]),
        ])


class ProjectsActive(LiveTable):
    javascript = [notify_client_js]
    update_topic = notify.TOPIC_PROJECTS
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
            Button(id='archive',
              action='%(id)s/archive',
              fields=[Icon(id='archive', icon_class='archive',
                label_text=_('archive')),
            ]),
            Button(id='edit',
              action='%(id)s/edit',
              fields=[Icon(id='edit', icon_class='edit',
                label_text=_('edit')),
            ]),
            Button(id='delete',
              action='%(id)s/delete',
              fields=[Icon(id='delete', icon_class='delete',
                label_text=_('delete')),
            ]),
        ])


class ProjectsArchived(LiveTable):
    javascript = [notify_client_js]
    update_topic = notify.TOPIC_PROJECTS
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
            Button(id='activate',
              action='%(id)s/activate',
              fields=[Icon(id='activate', icon_class='activate',
                label_text=_('activate')),
            ]),
        ])


class TableScenes(LiveTable):
    javascript = [notify_client_js]
    update_topic = notify.TOPIC_SCENES
    class fields(WidgetsList):
        thumbnail = Box(field_class='thumbnail', fields=[
            Image(label_text=_('thumbnail'), field_class='thumbnail',
              condition='data.has_preview',
              src=url('/repo/%(thumbnail)s'))
        ])
        namelink = Link(dest=url('/scene/%(proj_id)s/%(name)s/'), sort_default=True,
                        fields=[Text(id='name', label_text=_('name'))])
        description = Text()
        shots = StatusIconBox(fields=[
            StatusIcon(label_text='')
        ])
        actions = Box(
            condition='$.inArray(data.user_id, data.project.admin_ids)>=0',
            fields=[
              Button(id='edit',
                action=url('/scene/%(proj_id)s/%(name)s/edit'),
                fields=[Icon(id='edit', icon_class='edit',
                  label_text=_('edit')),
              ]),
              Button(id='delete',
                action=url('/scene/%(proj_id)s/%(name)s/delete'),
                fields=[Icon(id='delete', icon_class='delete',
                  label_text=_('delete')),
              ]),
        ])


class TableShots(LiveTable):
    javascript = [notify_client_js]
    update_topic = notify.TOPIC_SHOTS
    class fields(WidgetsList):
        thumbnail = Box(field_class='thumbnail', fields=[
            Image(label_text=_('thumbnail'), field_class='thumbnail',
              condition='data.has_preview',
              src=url('/repo/%(thumbnail)s'))
        ])
        namelink = Link(dest=url('/shot/%(proj_id)s/%(parent_name)s/%(name)s/'),
                        sort_default=True,
                        fields=[Text(id='name', label_text=_('name'))])
        description = Text()
        frames = Text()
        categories = Box(field_class='statusbox', fields=[
            Link(dest='%s#%s' % (
                          url('/shot/%(proj_id)s/%(parent_name)s/%(name)s'),
                          url('/asset/%(proj_id)s/%(container_type)s/%(id)s')),
              fields=[
                StatusIcon(id='item_status', label_text='%(item_name)s: %(item_status)s')
            ])
        ])
        actions = Box(
            condition='$.inArray(data.user_id, data.project.admin_ids)>=0',
            fields=[
            Button(id='edit',
              action=url('/shot/%(proj_id)s/%(parent_name)s/%(name)s/edit'),
              fields=[Icon(id='edit', icon_class='edit',
                label_text=_('edit')),
            ]),
            Button(id='delete',
              action=url('/shot/%(proj_id)s/%(parent_name)s/%(name)s/delete'),
              fields=[Icon(id='delete', icon_class='delete',
                label_text=_('delete')),
            ]),
        ])


class TableLibgroups(LiveTable):
    params = ['parent_id']
    javascript = [notify_client_js]
    update_topic = notify.TOPIC_LIBGROUPS
    class fields(WidgetsList):
        thumbnail = Box(field_class='thumbnail', fields=[
            Image(label_text=_('thumbnail'), field_class='thumbnail',
              condition='data.has_preview',
              src=url('/repo/%(thumbnail)s'))
        ])
        namelink = Link(dest=url('/libgroup/%(proj_id)s/%(id)s/'),
                        sort_default=True,
                        fields=[Text(id='name', label_text=_('name'))])
        description = Text()
        subgroups = StatusIconBox(fields=[
            StatusIcon(label_text='')
        ])
        categories = Box(field_class='statusbox', fields=[
            Link(dest='%s#%s' % (
                          url('/libgroup/%(proj_id)s/%(id)s'),
                          url('/asset/%(proj_id)s/%(container_type)s/%(id)s')),
              fields=[
                StatusIcon(id='item_status', label_text='%(item_name)s: %(item_status)s')
            ])
        ])
        actions = Box(
            condition='$.inArray(data.user_id, data.project.admin_ids)>=0',
            fields=[
              Button(id='edit',
                action=url('/libgroup/%(proj_id)s/%(id)s/edit'),
                fields=[Icon(id='edit', icon_class='edit',
                  label_text=_('edit')),
              ]),
              Button(id='delete',
                action=url('/libgroup/%(proj_id)s/%(id)s/delete'),
                fields=[Icon(id='delete', icon_class='delete',
                  label_text=_('delete')),
              ]),
        ])
    
    def update_params(self, d):
        super(TableLibgroups, self).update_params(d)
        d['update_condition'] = 'msg.ob.parent_id==%s' % (
                        d['parent_id'] and '"%s"' % d['parent_id'] or 'null')


class TableAssets(LiveTable):
    params = ['category']
    
    javascript = [notify_client_js]
    update_topic = notify.TOPIC_ASSETS
    class fields(WidgetsList):
        thumbnail = Box(field_class='thumbnail', fields=[
            Link(dest=url('/repo/%(proj_id)s/preview.png'),
              condition='data.has_preview', fields=[
              Image(label_text=_('preview'), field_class='thumbnail',
                src=url('/repo/%(thumbnail)s'))
            ])
        ])
        name = Box(fields=[
            Text(id='name', sort_default=True),
            Text(id='owner_id', field_class='owner',
              condition='data.checkedout',
              text='%s: %s' % (_('checkedout by'), '%(owner_user_name)s'),
              label_text='%(owner_id)s (%(owner_display_name)s)',
              )
        ])
        current_fmtver = Text(label_text=_('version'))
        status = StatusIcon(icon_class='asset', label_text=_('status: '))
        note = Box(fields=[
            Text(id='current_header', field_class='note_header',
              label_text=_('latest comment')),
            Text(id='current_summary', label_text=_('latest comment')),
        ])
        actions = Box(fields=[
            Button(id='history',
              action=url('/asset/%(proj_id)s/%(id)s'),
              fields=[Icon(id='history', icon_class='history',
                label_text=_('asset history')),
            ]),
            Button(id='addnote', icon_class='edit',
              label_text=_('add note'),
              action=url('/note/%(current_id)s/new'),
              fields=[Icon(id='addnote', icon_class='edit',
                label_text=_('add note')),
            ]),
            Button(id='checkout',
              condition=('!data.checkedout && !data.approved '
                         '&& ($.inArray(data.user_id, data.supervisor_ids)>=0 '
                         '|| $.inArray(data.user_id, data.artist_ids)>=0)'),
              action=url('/asset/%(proj_id)s/%(id)s/checkout'),
              fields=[Icon(id='checkout', icon_class='checkout',
                label_text=_('checkout')),
            ]),
            Button(id='release',
              condition=('data.checkedout && !data.submitted && !data.approved '
                         '&& (data.user_id==data.owner_id '
                         '|| $.inArray(data.user_id, data.supervisor_ids)>=0)'),
              action=url('/asset/%(proj_id)s/%(id)s/release'),
              fields=[Icon(id='release', icon_class='release',
                label_text=_('release')),
            ]),
            Button(id='publish',
              condition=('data.checkedout '
                         '&& data.user_id==data.owner_id'),
              action=url('/asset/%(proj_id)s/%(id)s/publish'),
              fields=[Icon(id='publish', icon_class='publish',
                label_text=_('publish a new version')),
            ]),
            Button(id='submit', icon_class='submit',
              condition=('data.checkedout && data.current_ver>0 '
                         '&& !data.submitted && !data.approved '
                         '&& data.user_id==data.owner_id'),
              action=url('/asset/%(proj_id)s/%(id)s/submit'),
              fields=[Icon(id='submit', icon_class='submit',
                label_text=_('submit for approval')),
            ]),
            Button(id='recall',
              condition=('data.submitted && !data.approved '
                         '&& data.user_id==data.owner_id'),
              action=url('/asset/%(proj_id)s/%(id)s/recall'),
              fields=[Icon(id='recall', icon_class='recall',
                label_text=_('recall submission')),
            ]),
            Button(id='sendback',
              condition=('data.submitted && !data.approved '
                         '&& $.inArray(data.user_id, data.supervisor_ids)>=0'),
              action=url('/asset/%(proj_id)s/%(id)s/sendback'),
              fields=[Icon(id='sendback', icon_class='sendback',
                label_text=_('send back for revisions')),
            ]),
            Button(id='approve',
              condition=('data.submitted && !data.approved '
                         '&& $.inArray(data.user_id, data.supervisor_ids)>=0'),
              action=url('/asset/%(proj_id)s/%(id)s/approve'),
              fields=[Icon(id='approve', icon_class='approve',
                label_text=_('approve')),
            ]),
            Button(id='revoke',
              condition=('data.approved '
                         '&& $.inArray(data.user_id, data.supervisor_ids)>=0'),
              action=url('/asset/%(proj_id)s/%(id)s/revoke'),
              fields=[Icon(id='revoke', icon_class='revoke',
                label_text=_('revoke approval')),
            ]),
            Link(id='download_link',
              condition='data.current_ver && data.current_ver>0',
              dest=url('/asset/%(proj_id)s/%(current_id)s/download'),
              fields=[
                Icon(id='download', icon_class='download',
                  label_text=_('download'),
                )
            ]),
            Button(id='delete',
              condition='$.inArray(data.user_id, data.project.admin_ids)>=0',
              action=url('/asset/%(proj_id)s/%(id)s/delete'),
              fields=[Icon(id='delete', icon_class='delete',
                label_text=_('delete')),
            ]),
        ])
    
    def update_params(self, d):
        super(TableAssets, self).update_params(d)
        d['update_condition'] = 'msg.ob.category.id=="%s"' % d['category']


class TableAssetHistory(LiveTable):
    class fields(WidgetsList):
        thumbnail = Box(field_class='thumbnail', fields=[
            Link(dest=url('/repo/%(preview_path)s'),
              condition='data.has_preview', fields=[
              Image(label_text=_('preview'), field_class='thumbnail',
                src=url('/repo/%(thumbnail)s'))
            ])
        ])
        fmtver = Text(label_text='ver')
        note = Box(fields=[
            Text(id='header', field_class='note_header',
              label_text=''),
            Box(id='lines', fields=[
                Text(id='item_line', label_text='')
            ]),
        ])
        actions = Box(fields=[
            Link(id='download_link',
              condition='data.ver && data.ver>0',
              dest=url('/asset/%(proj_id)s/%(id)s/download'),
              fields=[
                Icon(id='download', icon_class='download',
                  label_text=_('download'),
                )
            ]),
        ])


class TableJournal(LiveTable):
    params = ['curpage']
    javascript = [notify_client_js]
    update_topic = notify.TOPIC_JOURNAL
    class fields(WidgetsList):
        strftime = Text(label_text='date', sort_default=True,
                                                        sort_direction = 'desc')
        user_id = Text(label_text='user')
        text = Text()
    
    def update_params(self, d):
        super(TableJournal, self).update_params(d)
        d['update_condition'] = '%s==1' % d['curpage']


class TableNotes(LiveTable):
    params = ['annotable_id']
    javascript = [notify_client_js]
    update_topic = notify.TOPIC_NOTES
    class fields(WidgetsList):
        user_name = Text(field_class='note_header', label_text=_('user name'))
        strftime = Text(field_class='note_header', label_text=_('date'),
                        sort_default=True, sort_direction='desc')
        lines = Box(fields=[
            Text(id='text', label_text='')
        ])
        actions = Box(
            condition='$.inArray(data.user_id, data.project.admin_ids)>=0',
            fields=[
              Button(id='pin',
                condition='!data.sticky',
                action=url('/note/%(id)s/pin'),
                fields=[Icon(id='pin', icon_class='pin',
                  label_text=_('pin note')),
              ]),
              Button(id='unpin',
                condition='data.sticky',
                action=url('/note/%(id)s/unpin'),
                fields=[Icon(id='unpin', icon_class='unpin',
                  label_text=_('un-pin note')),
              ]),
        ])
    
    def update_params(self, d):
        super(TableNotes, self).update_params(d)
        d['update_condition'] = 'msg.annotable_id=="%s"' % d['annotable_id']


############################################################
# Live lists
############################################################
class ListProjects(LiveList):
    params = ['user_id']
    javascript = [notify_client_js]
    update_topic = notify.TOPIC_PROJECTS
    class fields(WidgetsList):
        name = Link(dest=url('/project/%(id)s'), fields=[
            Text(id='name', label_text='%(description)s')
        ])
    
    def update_params(self, d):
        super(ListProjects, self).update_params(d)
        d['update_condition'] = ('$.inArray("%s", msg.ob.user_ids) > -1' %
                                                                d['user_id'])


############################################################
# Live boxes
############################################################
class BoxTags(LiveBox):
    params = ['taggable_id']
    container_class = 'tagbox'
    javascript = [notify_client_js]
    update_topic = notify.TOPIC_TAGS
    class fields(WidgetsList):
        id = Box(fields=[
            Text(id='id', label_text=''),
            Button(id='remove',
              condition='$.inArray(data.user_id, data.project.admin_ids)>=0',
              action=url('/tag/%(taggable_id)s/%(id)s/remove'),
              fields=[Icon(id='remove', icon_class='delete',
                label_text=_('remove')),
            ]),
            Text(id='separator', label_text='', text=', '),
        ])
    
    def update_params(self, d):
        super(BoxTags, self).update_params(d)
        d['update_condition'] = 'msg.taggable_id=="%s"' % d['taggable_id']


statusbox_js = JSSource(src='''
    wrap_functions = function(func, box_id, item, show_update, extra_data) {
        $.each(item.parent.categories, function (i, parent_cat) {
            if (parent_cat.id==item.category.id)
                cat = parent_cat;
        });
        if (typeof(cat) != 'udefined')
            func(box_id, cat, show_update, extra_data);
    }
    
    add_categories = function(box_id, item, show_update, extra_data) {
        if (typeof(item.ordering)!='undefined')   // 'item' is a category
            lw.livebox.add(box_id, item, show_update, extra_data);
        else    // 'item' is an asset
            wrap_functions(lw.livebox.add, box_id, item, false, extra_data);
    }
    delete_categories = function(box_id, item, show_update, extra_data) {
        if (typeof(item.ordering)!='undefined')   // 'item' is a category
            lw.livebox.delete(box_id, item, show_update, extra_data);
        else    // 'item' is an asset
            wrap_functions(lw.livebox.delete, box_id, item, false, extra_data);
    }
    update_categories = function(box_id, item, show_update, extra_data) {
        wrap_functions(lw.livebox.update, box_id, item, false, extra_data);
    }
''')


class BoxScenesStatus(LiveBox):
    params = ['proj_id']
    container_class = 'statusbox'
    update_topic = notify.TOPIC_SCENES
    show_update = False
    
    class fields(WidgetsList):
        link = Link(dest=url('/scene/%(proj_id)s/%(name)s'),
            fields=[
              StatusIcon(id='status', label_text='%(name)s: %(status)s')
        ])
    
    def update_params(self, d):
        super(BoxScenesStatus, self).update_params(d)
        d['update_condition'] = 'msg.ob.proj_id=="%s"' % d['proj_id']


class BoxShotsStatus(LiveBox):
    params = ['scene_id']
    container_class = 'statusbox'
    update_topic = notify.TOPIC_SHOTS
    show_update = False
    
    class fields(WidgetsList):
        link = Link(dest=url('/shot/%(proj_id)s/%(parent_name)s/%(name)s'),
            fields=[
              StatusIcon(id='status', label_text='%(name)s: %(status)s')
        ])
    
    def update_params(self, d):
        super(BoxShotsStatus, self).update_params(d)
        d['update_condition'] = 'msg.ob.parent_id=="%s"' % d['scene_id']


class BoxLibgroupsStatus(LiveBox):
    params = ['libgroup_id']
    container_class = 'statusbox'
    update_topic = notify.TOPIC_LIBGROUPS
    show_update = False
    
    class fields(WidgetsList):
        link = Link(dest=url('/libgroup/%(proj_id)s/%(id)s'),
            fields=[
              StatusIcon(id='status', label_text='%(name)s: %(status)s')
        ])
    
    def update_params(self, d):
        super(BoxLibgroupsStatus, self).update_params(d)
        libgroup_id = d['libgroup_id'] and '"%s"' % d['libgroup_id'] or 'null'
        d['update_condition'] = 'msg.ob.parent_id==%s' % libgroup_id


class BoxCategoriesStatus(LiveBox):
    params = ['container_id']
    javascript = [statusbox_js]
    container_class = 'statusbox'
    update_topic = notify.TOPIC_ASSETS
    update_functions = ('{"added": add_categories,'
                        ' "deleted": delete_categories,'
                        ' "updated": update_categories}')
    show_update = False
    
    class fields(WidgetsList):
        category = Link(
              dest='#/asset/%(proj_id)s/%(container_type)s/%(container_id)s',
              fields=[
                StatusIcon(id='status', label_text='%(name)s: %(status)s')
        ])
    
    def update_params(self, d):
        super(BoxCategoriesStatus, self).update_params(d)
        d['update_condition'] = 'msg.ob.parent_id=="%s"' % d['container_id']


class BoxStatus(LiveBox):
    params = ['container_id', 'category_id']
    javascript = [statusbox_js]
    container_class = 'statusbox'
    update_topic = notify.TOPIC_ASSETS
    update_functions = ('{"added": add_categories,'
                        ' "deleted": delete_categories,'
                        ' "updated": update_categories}')
    show_update = False
    
    class fields(WidgetsList):
        status = StatusIcon(label_text='%(name)s: %(status)s')
    
    def update_params(self, d):
        super(BoxStatus, self).update_params(d)
        d['update_condition'] = ('msg.ob.parent_id=="%s" && '
            'msg.ob.category.id=="%s"' % (d['container_id'], d['category_id']))


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
    params = ['target', 'queue', 'submitter']
    template = 'mako:spam.templates.widgets.upload'
    upload_js = JSLink(link=url('/js/widgets/upload.js'))
    javascript = [upload_js]
    
    target = url('/upload')
    queue = '#upload_queue'
    submitter = '.submitbutton'


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

