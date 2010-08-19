# -*- coding: utf-8 -*-
#
# This file is part of SPAM (Spark Project & Asset Manager).
#
# SPAM is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# SPAM is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with SPAM.  If not, see <http://www.gnu.org/licenses/>.
#
# Original Copyright (c) 2010, Lorenzo Pierfederici <lpierfederici@gmail.com>
# Contributor(s): 
#
"""Custom ToscaWidgets for SPAM."""

from tg import config, url
from tg import app_globals as G
from pylons.i18n import ugettext as _, lazy_ugettext as l_
from tw.api import Widget, WidgetsList, JSLink, JSSource, js_function
from tw.forms import TableForm, TextField, TextArea, HiddenField, FormField
from tw.forms import CalendarDatePicker, SingleSelectField, FileField, Spacer
from tw.forms import PasswordField, MultipleSelectField
from tw.forms.validators import All, Any, Regex, MaxLength, NotEmpty, Int
from tw.forms.validators import Schema
import tw2.core as twc, tw2.forms as twf
from tw2.core import StringLengthValidator as StringLength
from spam.lib.validators import CategoryNamingConvention
from livewidgets import LiveTable, LiveBox, LiveList
from livewidgets import LiveWidget, Box, Button, Icon, Text, Link, Image
from spam.lib.notifications import notify


############################################################
# Custom Live widgets
############################################################
class StatusIcon(LiveWidget):
    """Custom livewidget to show a status icon."""
    params = ['icon_class']
    template = 'mako:spam.templates.widgets.statusicon'
    
    field_class = 'lw_status'
    show_header = False
    sortable = False


class StatusIconBox(LiveWidget):
    """Custom livewidget to show a box of status icons."""
    params = ['icon_class', 'dest']
    template = 'mako:spam.templates.widgets.statusiconbox'
    
    field_class = 'statusiconbox'
    show_header = False
    sortable = False


############################################################
# Live tables
############################################################
class TableUsers(LiveTable):
    """User livetable."""
    update_topic = notify.TOPIC_USERS
    class fields(WidgetsList):
        domain = Text()
        user_name = Text(sort_default=True)
        display_name = Text()
        actions = Box(fields=[
            Button(id='edit',
              action=url('/user/%(user_name)s/edit'),
              fields=[Icon(id='edit', icon_class='edit',
                label_text='edit'),
            ]),
            Button(id='delete',
              action=url('/user/%(user_name)s/delete'),
              fields=[Icon(id='delete', icon_class='delete',
                label_text='delete'),
            ]),
        ])


class TableGroupUsers(LiveTable):
    """Group users livetable."""
    update_topic = notify.TOPIC_GROUPS
    class fields(WidgetsList):
        user_name = Text(sort_default=True)
        display_name = Text()
        actions = Box(fields=[
            Button(id='remove',
              action=url(
                '/user/%(user_name)s/%(group_name)s/remove_from_group'),
              fields=[Icon(id='delete', icon_class='delete',
                label_text='remove'),
            ]),
        ])
    
    def update_params(self, d):
        super(TableGroupUsers, self).update_params(d)
        d['update_condition'] = 'msg.group_name=="%s"' % (
                                                d['extra_data']['group_name'])


class TableProjectAdmins(LiveTable):
    """Project administrators livetable."""
    update_topic = notify.TOPIC_PROJECT_ADMINS
    class fields(WidgetsList):
        user_name = Text(sort_default=True)
        display_name = Text()
        actions = Box(fields=[
            Button(id='remove',
              action=url('/user/%(proj)s/%(user_name)s/remove_admin'),
              fields=[Icon(id='delete', icon_class='delete',
                label_text='remove'),
            ]),
        ])
    
    def update_params(self, d):
        super(TableProjectAdmins, self).update_params(d)
        d['update_condition'] = 'msg.proj=="%s"' % d['extra_data']['proj']


class TableProjectSupervisors(LiveTable):
    """Project supervisors livetable."""
    update_topic = notify.TOPIC_PROJECT_SUPERVISORS
    class fields(WidgetsList):
        user_name = Text(sort_default=True)
        display_name = Text()
        actions = Box(fields=[
            Button(id='remove',
              action=url(
                    '/user/%(proj)s/%(cat)s/%(user_name)s/remove_supervisor'),
              fields=[Icon(id='delete', icon_class='delete',
                label_text='remove'),
            ]),
        ])
    
    def update_params(self, d):
        super(TableProjectSupervisors, self).update_params(d)
        d['update_condition'] = 'msg.proj=="%s" && msg.cat=="%s"' % (
                            (d['extra_data']['proj'], d['extra_data']['cat']))


class TableProjectArtists(LiveTable):
    """Project artists livetable."""
    update_topic = notify.TOPIC_PROJECT_ARTISTS
    class fields(WidgetsList):
        user_name = Text(sort_default=True)
        display_name = Text()
        actions = Box(fields=[
            Button(id='remove', icon_class='delete',
              label_text='remove',
              action=url('/user/%(proj)s/%(cat)s/%(user_name)s/remove_artist'),
              fields=[Icon(id='delete', icon_class='delete',
                label_text='remove'),
            ]),
        ])
    
    def update_params(self, d):
        super(TableProjectArtists, self).update_params(d)
        d['update_condition'] = 'msg.proj=="%s" && msg.cat=="%s"' % (
                            (d['extra_data']['proj'], d['extra_data']['cat']))


class TableCategories(LiveTable):
    """Category livetable."""
    update_topic = notify.TOPIC_CATEGORIES
    class fields(WidgetsList):
        ordering = Text(sort_default=True)
        id = Text()
        naming_convention = Text()
        actions = Box(fields=[
            Button(id='edit',
              action=url('/category/%(id)s/edit'),
              fields=[Icon(id='edit', icon_class='edit',
                label_text='edit'),
            ]),
            Button(id='delete',
              label_text='delete',
              action=url('/category/%(id)s/delete'),
              fields=[Icon(id='delete', icon_class='delete',
                label_text='delete'),
            ]),
        ])


class ProjectsActive(LiveTable):
    """Active projects livetable."""
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
                label_text='archive'),
            ]),
            Button(id='edit',
              action='%(id)s/edit',
              fields=[Icon(id='edit', icon_class='edit',
                label_text='edit'),
            ]),
            Button(id='delete',
              action='%(id)s/delete',
              fields=[Icon(id='delete', icon_class='delete',
                label_text='delete'),
            ]),
        ])


class ProjectsArchived(LiveTable):
    """Archived projects livetable."""
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
                label_text='activate'),
            ]),
        ])


class TableScenes(LiveTable):
    """Scene livetable."""
    update_topic = notify.TOPIC_SCENES
    class fields(WidgetsList):
        thumbnail = Box(field_class='thumbnail', fields=[
            Image(label_text='thumbnail', field_class='thumbnail',
              condition='data.has_preview',
              src=url('/repo/%(thumbnail)s'))
        ])
        namelink = Link(dest=url('/scene/%(proj_id)s/%(name)s/'), sort_default=True,
                        fields=[Text(id='name', label_text='name')])
        description = Text()
        shots = StatusIconBox(
            dest=url('/shot/%(proj_id)s/%(parent_name)s/%(name)s/'),
            fields=[
              StatusIcon(label_text='')
        ])
        actions = Box(
            condition='$.inArray(data.user_id, data.project.admin_ids)>=0',
            fields=[
              Button(id='edit',
                action=url('/scene/%(proj_id)s/%(name)s/edit'),
                fields=[Icon(id='edit', icon_class='edit',
                  label_text='edit'),
              ]),
              Button(id='delete',
                action=url('/scene/%(proj_id)s/%(name)s/delete'),
                fields=[Icon(id='delete', icon_class='delete',
                  label_text='delete'),
              ]),
        ])


class TableShots(LiveTable):
    """Shot livetable."""
    update_topic = notify.TOPIC_SHOTS
    class fields(WidgetsList):
        thumbnail = Box(field_class='thumbnail', fields=[
            Image(label_text='thumbnail', field_class='thumbnail',
              condition='data.has_preview',
              src=url('/repo/%(thumbnail)s'))
        ])
        namelink = Link(dest=url('/shot/%(proj_id)s/%(parent_name)s/%(name)s/'),
                        sort_default=True,
                        fields=[Text(id='name', label_text='name')])
        description = Text()
        frames = Text()
        categories = Box(field_class='statusiconbox', fields=[
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
                label_text='edit'),
            ]),
            Button(id='delete',
              action=url('/shot/%(proj_id)s/%(parent_name)s/%(name)s/delete'),
              fields=[Icon(id='delete', icon_class='delete',
                label_text='delete'),
            ]),
        ])


class TableLibgroups(LiveTable):
    """Libgroup livetable."""
    params = ['parent_id']
    update_topic = notify.TOPIC_LIBGROUPS
    class fields(WidgetsList):
        thumbnail = Box(field_class='thumbnail', fields=[
            Image(label_text='thumbnail', field_class='thumbnail',
              condition='data.has_preview',
              src=url('/repo/%(thumbnail)s'))
        ])
        namelink = Link(dest=url('/libgroup/%(proj_id)s/%(id)s/'),
                        sort_default=True,
                        fields=[Text(id='name', label_text='name')])
        description = Text()
        subgroups = StatusIconBox(
            dest=url('/libgroup/%(proj_id)s/%(id)s'),
            fields=[
              StatusIcon(label_text='')
        ])
        categories = Box(field_class='statusiconbox', fields=[
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
                  label_text='edit'),
              ]),
              Button(id='delete',
                action=url('/libgroup/%(proj_id)s/%(id)s/delete'),
                fields=[Icon(id='delete', icon_class='delete',
                  label_text='delete'),
              ]),
        ])
    
    def update_params(self, d):
        super(TableLibgroups, self).update_params(d)
        d['update_condition'] = 'msg.ob.parent_id==%s' % (
                        d['parent_id'] and '"%s"' % d['parent_id'] or 'null')


class TableAssets(LiveTable):
    """Asset livetable."""
    params = ['category']
    
    update_topic = notify.TOPIC_ASSETS
    class fields(WidgetsList):
        thumbnail = Box(field_class='thumbnail status %(status)s', fields=[
            Link(dest=url('/repo/%(proj_id)s/preview.png'),
              condition='data.has_preview', fields=[
              Image(label_text='preview', field_class='thumbnail',
                src=url('/repo/%(thumbnail)s'))
            ])
        ])
        name = Box(field_class='status %(status)s', fields=[
            Text(id='name', sort_default=True),
            Text(id='owner_id', field_class='owner',
              condition='data.checkedout',
              text='%s: %s' % ('checkedout by', '%(owner_user_name)s'),
              label_text='%(owner_id)s (%(owner_display_name)s)',
              )
        ])
        current_fmtver = Text(field_class='status %(status)s', label_text='version')
        status = StatusIcon(field_class='status %(status)s', icon_class='asset',
                                                    label_text='status: ')
        note = Box(field_class='status %(status)s', fields=[
            Text(id='current_header', field_class='note_header',
              label_text='latest comment'),
            Text(id='current_summary', label_text='latest comment'),
        ])
        actions = Box(field_class='status %(status)s', fields=[
            Button(id='history',
              action=url('/asset/%(proj_id)s/%(id)s'),
              fields=[Icon(id='history', icon_class='history',
                label_text='asset history'),
            ]),
            Button(id='addnote', icon_class='edit',
              label_text='add note',
              action=url('/note/%(proj_id)s/%(current_id)s/new'),
              fields=[Icon(id='addnote', icon_class='edit',
                label_text='add note'),
            ]),
            Button(id='checkout',
              condition=('!data.checkedout && !data.approved '
                         '&& ($.inArray(data.user_id, data.supervisor_ids)>=0 '
                         '|| $.inArray(data.user_id, data.artist_ids)>=0)'),
              action=url('/asset/%(proj_id)s/%(id)s/checkout'),
              fields=[Icon(id='checkout', icon_class='checkout',
                label_text='checkout'),
            ]),
            Button(id='release',
              condition=('data.checkedout && !data.submitted && !data.approved '
                         '&& (data.user_id==data.owner_id '
                         '|| $.inArray(data.user_id, data.supervisor_ids)>=0)'),
              action=url('/asset/%(proj_id)s/%(id)s/release'),
              fields=[Icon(id='release', icon_class='release',
                label_text='release'),
            ]),
            Button(id='publish',
              condition=('data.checkedout '
                         '&& data.user_id==data.owner_id'),
              action=url('/asset/%(proj_id)s/%(id)s/publish'),
              fields=[Icon(id='publish', icon_class='publish',
                label_text='publish a new version'),
            ]),
            Button(id='submit', icon_class='submit',
              condition=('data.checkedout && data.current_ver>0 '
                         '&& !data.submitted && !data.approved '
                         '&& data.user_id==data.owner_id'),
              action=url('/asset/%(proj_id)s/%(id)s/submit'),
              fields=[Icon(id='submit', icon_class='submit',
                label_text='submit for approval'),
            ]),
            Button(id='recall',
              condition=('data.submitted && !data.approved '
                         '&& data.user_id==data.owner_id'),
              action=url('/asset/%(proj_id)s/%(id)s/recall'),
              fields=[Icon(id='recall', icon_class='recall',
                label_text='recall submission'),
            ]),
            Button(id='sendback',
              condition=('data.submitted && !data.approved '
                         '&& $.inArray(data.user_id, data.supervisor_ids)>=0'),
              action=url('/asset/%(proj_id)s/%(id)s/sendback'),
              fields=[Icon(id='sendback', icon_class='sendback',
                label_text='send back for revisions'),
            ]),
            Button(id='approve',
              condition=('data.submitted && !data.approved '
                         '&& $.inArray(data.user_id, data.supervisor_ids)>=0'),
              action=url('/asset/%(proj_id)s/%(id)s/approve'),
              fields=[Icon(id='approve', icon_class='approve',
                label_text='approve'),
            ]),
            Button(id='revoke',
              condition=('data.approved '
                         '&& $.inArray(data.user_id, data.supervisor_ids)>=0'),
              action=url('/asset/%(proj_id)s/%(id)s/revoke'),
              fields=[Icon(id='revoke', icon_class='revoke',
                label_text='revoke approval'),
            ]),
            Link(id='download_link',
              condition='data.current_ver && data.current_ver>0',
              dest=url('/asset/%(proj_id)s/%(current_id)s/download'),
              fields=[
                Icon(id='download', icon_class='download',
                  label_text='download',
                )
            ]),
            Button(id='delete',
              condition='$.inArray(data.user_id, data.project.admin_ids)>=0',
              action=url('/asset/%(proj_id)s/%(id)s/delete'),
              fields=[Icon(id='delete', icon_class='delete',
                label_text='delete'),
            ]),
        ])
    
    def update_params(self, d):
        super(TableAssets, self).update_params(d)
        d['update_condition'] = 'msg.ob.category.id=="%s"' % d['category']


class TableAssetHistory(LiveTable):
    """Asset history livetable."""
    class fields(WidgetsList):
        thumbnail = Box(field_class='thumbnail', fields=[
            Link(dest=url('/repo/%(preview_path)s'),
              condition='data.has_preview', fields=[
              Image(label_text='preview', field_class='thumbnail',
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
                  label_text='download',
                )
            ]),
        ])


class TableJournal(LiveTable):
    """Journal entries livetable."""
    params = ['curpage']
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
    """Note livetable."""
    params = ['annotable_id']
    update_topic = notify.TOPIC_NOTES
    class fields(WidgetsList):
        user_name = Text(field_class='note_header', label_text='user name')
        strftime = Text(field_class='note_header', label_text='date',
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
                  label_text='pin note'),
              ]),
              Button(id='unpin',
                condition='data.sticky',
                action=url('/note/%(id)s/unpin'),
                fields=[Icon(id='unpin', icon_class='unpin',
                  label_text='un-pin note'),
              ]),
        ])
    
    def update_params(self, d):
        super(TableNotes, self).update_params(d)
        d['update_condition'] = 'msg.annotable_id=="%s"' % d['annotable_id']


############################################################
# Live lists
############################################################
class ListProjects(LiveList):
    """Project livelist."""
    params = ['user_id']
    update_topic = notify.TOPIC_PROJECTS
    class fields(WidgetsList):
        name = Link(dest=url('/project/%(id)s'), field_class='%(id)s', fields=[
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
    """Tag livebox."""
    params = ['taggable_id']
    container_class = 'tagbox'
    update_topic = notify.TOPIC_TAGS
    class fields(WidgetsList):
        id = Box(fields=[
            Text(id='id', label_text=''),
            Button(id='remove',
              condition='$.inArray(data.user_id, data.project.admin_ids)>=0',
              action=url('/tag/%(taggable_id)s/%(id)s/remove'),
              fields=[Icon(id='remove', icon_class='delete',
                label_text='remove'),
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
    """Scene status livebox."""
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
    """Shot status livebox."""
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
    """Libgroup status livebox."""
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
    """Asset categories status livebox."""
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
    """Category status livebox."""
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

# defaults for input fields
SEL_SIZE = 10
TEXT_AREA_COLS = 30
TEXT_AREA_ROWS = 3

# base class
class RestForm(twf.TableForm):
    """Base class for forms that submit data to a custom REST method via the
    ``_method`` parameter
    """
    custom_method = twc.Param('The custom REST method to use for submitting '
        'the form', default='POST')
    custom_method_field = twf.IgnoredField(name='_method')
    submit = twf.SubmitButton(id='submit', value='Submit')

    def prepare(self):
        if not self.child.children.custom_method_field.value:
            self.child.children.custom_method_field.value = self.custom_method
        super(RestForm, self).prepare()


# User
class FormUserNew(RestForm):
    """New user form."""
    user_name = twf.TextField(validator=StringLength(max=16, required=True))
    display_name = twf.TextField(validator=StringLength(max=255, required=True))
    password = twf.PasswordField(validator=StringLength(max=80, required=True))


class FormUserEdit(RestForm):
    """Edit user form."""
    custom_method = 'PUT'
    user_id = twf.HiddenField()
    user_name_ = twf.LabelField()
    display_name = twf.TextField(validator=StringLength(max=255, required=True))


class FormUserConfirm(RestForm):
    """Generic user confirmation form."""
    user_id = twf.HiddenField()
    user_name_ = twf.LabelField()
    display_name_ = twf.LabelField()


class FormUserAddToGroup(RestForm):
    """Add user to group form."""
    custom_method = 'ADD_TO_GROUP'
    group_id = twf.HiddenField()
    userids = twf.MultipleSelectField(label='Users', options=[], size=SEL_SIZE)


class FormUserAddAdmins(RestForm):
    """Add admin to project form."""
    custom_method = 'ADD_ADMINS'
    proj = twf.HiddenField()
    userids = twf.MultipleSelectField(label='Users', options=[], size=SEL_SIZE)


class FormUserAddToCategory(RestForm):
    """Add user to category form."""
    proj = twf.HiddenField()
    category_id = twf.HiddenField()
    userids = twf.MultipleSelectField(label='Users', options=[], size=SEL_SIZE)


# Category
class FormCategoryNew(RestForm):
    """New category form."""
    category_id = twf.TextField(validator=twc.All(StringLength(max=30),
                    twc.RegexValidator(regex=G.pattern_name), required=True))
    ordering = twf.TextField(validator=twc.IntValidator)
    naming_convention = twf.TextField(validator=StringLength(max=255))


class FormCategoryEdit(RestForm):
    """Edit category form."""
    custom_method = 'PUT'
    category_id = twf.HiddenField()
    id_ = twf.LabelField()
    ordering = twf.TextField(validator=twc.IntValidator)
    naming_convention = twf.TextField(validator=StringLength(max=255))


class FormCategoryConfirm(RestForm):
    """Generic category confirmation form."""
    category_id = twf.HiddenField()
    id_ = twf.LabelField()
    ordering_ = twf.LabelField()
    naming_convention_ = twf.LabelField()


# Tag
class FormTagNew(RestForm):
    """New tag form."""
    taggable_id = twf.HiddenField()
    current_tags_ = twf.LabelField()
    tagids = twf.MultipleSelectField(label='Tags', options=[], size=SEL_SIZE)
    new_tags = twf.TextField(validator=twc.RegexValidator(regex=G.pattern_tags))


class FormTagConfirm(RestForm):
    """Generic tag confirmation form."""
    tag_id = twf.HiddenField()


class FormTagRemove(RestForm):
    """Remove tag form."""
    custom_method = 'REMOVE'
    taggable_id = twf.HiddenField()
    tagids = twf.MultipleSelectField(label='Tags', options=[], size=SEL_SIZE)


# Note
class FormNoteNew(RestForm):
    """New note form."""
    proj = twf.HiddenField()
    annotable_id = twf.HiddenField()
    text = twf.TextArea(cols=TEXT_AREA_COLS, rows=TEXT_AREA_ROWS,
                                                        validator=twc.Required)
        

class FormNoteConfirm(RestForm):
    """Generic note confirmation form."""
    proj = twf.HiddenField()
    note_id = twf.HiddenField()
    text_ = twf.LabelField()


# Project
class FormProjectNew(RestForm):
    """New project form."""
    proj = twf.TextField(label='id', validator=twc.All(StringLength(max=15),
                    twc.RegexValidator(regex=G.pattern_name), required=True))
    project_name = twf.TextField(label='Name', validator=StringLength(max=40))
    description = twf.TextArea(cols=TEXT_AREA_COLS, rows=TEXT_AREA_ROWS)


class FormProjectEdit(RestForm):
    """Edit project form."""
    custom_method = 'PUT'
    proj = twf.HiddenField()
    id_ = twf.LabelField()
    project_name = twf.TextField(label='Name', validator=StringLength(max=40))
    description = twf.TextArea(cols=TEXT_AREA_COLS, rows=TEXT_AREA_ROWS)


class FormProjectConfirm(RestForm):
    """Generic project confirmation form."""
    proj = twf.HiddenField()
    id_ = twf.LabelField()
    project_name_ = twf.LabelField(label='Name')
    description_ = twf.LabelField()


# Scene
class FormSceneNew(TableForm):
    """New scene form."""
    class fields(WidgetsList):
        proj = HiddenField(validator=NotEmpty)
        project_ = TextField(validator=None, disabled=True)
        sc = TextField(label_text='name', validator=All(Regex(G.pattern_name,
                                                not_empty=True), MaxLength(15)))
        description = TextArea(cols=30, rows=3)


class FormSceneEdit(TableForm):
    """Edit scene form."""
    class fields(WidgetsList):
        _method = HiddenField(default='PUT', validator=None)
        proj = HiddenField(validator=NotEmpty)
        sc = HiddenField(validator=NotEmpty)
        project_ = TextField(validator=None, disabled=True)
        name_ = TextField(validator=None, disabled=True)
        description = TextArea(cols=30, rows=3)


class FormSceneConfirm(TableForm):
    """Generic scene confirmation form."""
    class fields(WidgetsList):
        _method = HiddenField(default='', validator=None)
        proj = HiddenField(validator=NotEmpty)
        sc = HiddenField(validator=NotEmpty)
        project_ = TextField(validator=None, disabled=True)
        name_ = TextField(validator=None, disabled=True)
        description_ = TextArea(cols=30, rows=3, disabled=True, validator=None)


# Shot
class FormShotNew(TableForm):
    """New shot form."""
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
    """Edit shot form."""
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
    """Generic shot confirmation form."""
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
    """New libgroup form."""
    class fields(WidgetsList):
        proj = HiddenField(validator=NotEmpty)
        parent_id = HiddenField()
        project_ = TextField(validator=None, disabled=True)
        parent_ = TextField(validator=None, disabled=True)
        name = TextField(validator=All(Regex(G.pattern_name, not_empty=True),
                                       MaxLength(15)))
        description = TextArea(cols=30, rows=3)


class FormLibgroupEdit(TableForm):
    """Edit libgroup form."""
    class fields(WidgetsList):
        _method = HiddenField(default='PUT', validator=None)
        proj = HiddenField(validator=NotEmpty)
        libgroup_id = HiddenField(validator=NotEmpty)
        project_ = TextField(validator=None, disabled=True)
        name_ = TextField(validator=None, disabled=True)
        description = TextArea(cols=30, rows=3)


class FormLibgroupConfirm(TableForm):
    """Generic libgroup confirmation form."""
    class fields(WidgetsList):
        _method = HiddenField(default='', validator=None)
        proj = HiddenField(validator=NotEmpty)
        libgroup_id = HiddenField(validator=NotEmpty)
        project_ = TextField(validator=None, disabled=True)
        name_ = TextField(validator=None, disabled=True)
        description_ = TextArea(cols=30, rows=3, disabled=True, validator=None)


# Asset
class FormAssetNew(TableForm):
    """New asset form."""
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
    """Edit asset form."""
    class fields(WidgetsList):
        _method = HiddenField(default='PUT', validator=None)
        proj = HiddenField(validator=NotEmpty)
        project_ = TextField(validator=None, disabled=True)


class FormAssetConfirm(TableForm):
    """Generic asset confirmation form."""
    class fields(WidgetsList):
        _method = HiddenField(default='', validator=None)
        proj = HiddenField(validator=NotEmpty)
        project_ = TextField(validator=None, disabled=True)
        asset_id = HiddenField(validator=NotEmpty)
        container_ = TextField(validator=None, disabled=True)
        category_ = TextField(validator=None, disabled=True)
        name_ = TextField(validator=None, disabled=True)


class Upload(FormField):
    """Advanced upload field for the publish asset form.
    
    An ``Upload`` field uploads file to the server as they are selected
    (or dragged onto it) and shows a progress bar for the upload."""
    params = ['target', 'queue', 'submitter', 'ext']
    template = 'mako:spam.templates.widgets.upload'
    upload_js = JSLink(link=url('/js/widgets/upload.js'))
    javascript = [upload_js]
    
    target = url('/upload')
    queue = '#upload_queue'
    submitter = '.submitbutton'
    ext = None


class FormAssetPublish(TableForm):
    """Publish asset form."""
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
    """Asset status form."""
    class fields(WidgetsList):
        _method = HiddenField(default='', validator=None)
        proj = HiddenField(validator=NotEmpty)
        project_ = TextField(validator=None, disabled=True)
        asset_id = HiddenField(validator=NotEmpty)
        container_ = TextField(validator=None, disabled=True)
        category_ = TextField(validator=None, disabled=True)
        name_ = TextField(validator=None, disabled=True)
        comment = TextArea(cols=30, rows=3)

