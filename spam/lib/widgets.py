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
import tw2.core as twc, tw2.forms as twf
import tw2.livewidgets as twl
from tw2.core import StringLengthValidator as StringLength, MatchValidator
from spam.lib.validators import CategoryNamingConvention
from spam.lib import notifications


############################################################
# Custom Live widgets
############################################################
#class StatusIcon(LiveWidget):
#    """Custom livewidget to show a status icon."""
#    params = ['icon_class']
#    template = 'mako:spam.templates.widgets.statusicon'
#    
#    css_class = 'lw_status'
#    show_header = False
#    sortable = False


#class StatusIconBox(LiveWidget):
#    """Custom livewidget to show a box of status icons."""
#    params = ['icon_class', 'dest']
#    template = 'mako:spam.templates.widgets.statusiconbox'
#    
#    css_class = 'statusiconbox'
#    show_header = False
#    sortable = False


############################################################
# Live tables
############################################################
class TableUsers(twl.LiveTable):
    """User livetable."""
    update_topic = notifications.TOPIC_USERS
    show_headers = False
    domain = twl.Text()
    user_name = twl.Text(sort_default=True)
    display_name = twl.Text()
    actions = twl.Box(
        children=[
            twl.Button(id='edit',
                action=url('/user/%(user_name)s/edit'),
                dialog=True,
                children=[
                    twl.Icon(id='edit',
                        icon_class='icon_edit',
                        help_text='edit'),
            ]),
            twl.Button(id='delete',
                action=url('/user/%(user_name)s/delete'),
                dialog=True,
                children=[
                    twl.Icon(id='delete',
                        icon_class='icon_delete',
                        help_text='delete'),
            ]),
    ])


class TableGroupUsers(twl.LiveTable):
    """Group users livetable."""
    update_topic = notifications.TOPIC_GROUPS
    show_headers = False
    user_name = twl.Text(sort_default=True)
    display_name = twl.Text()
    actions = twl.Box(
        children=[
            twl.Button(id='remove',
                action=url(
                    '/user/%(user_name)s/%(group_name)s/remove_from_group'),
                children=[
                    twl.Icon(id='remove',
                        icon_class='icon_delete',
                        help_text='remove'),
            ]),
    ])


class TableProjectUsers(twl.LiveTable):
    """Base class for project users livetables."""
    show_headers = False
    user_name = twl.Text(sort_default=True)
    display_name = twl.Text()
    actions = twl.Box(
        children=[
            twl.Button(id='remove',
                children=[
                    twl.Icon(id='remove',
                        icon_class='icon_delete',
                        help_text='remove'),
            ]),
    ])


class TableProjectAdmins(TableProjectUsers):
    """Project administrators livetable."""
    update_topic = notifications.TOPIC_PROJECT_ADMINS

    @classmethod
    def post_define(cls):
        cls.child.children[2].children[0].action = url(
                    '/user/%(proj)s/%(user_name)s/remove_admin')


class TableProjectSupervisors(TableProjectUsers):
    """Project users livetable."""
    update_topic = notifications.TOPIC_PROJECT_SUPERVISORS

    @classmethod
    def post_define(cls):
        cls.child.children[2].children[0].action = url(
                    '/user/%(proj)s/%(cat)s/%(user_name)s/remove_supervisor')


class TableProjectArtists(TableProjectUsers):
    """Project artists livetable."""
    update_topic = notifications.TOPIC_PROJECT_ARTISTS

    @classmethod
    def post_define(cls):
        cls.child.children[2].children[0].action = url(
                    '/user/%(proj)s/%(cat)s/%(user_name)s/remove_artist')


class TableCategories(twl.LiveTable):
    """Category livetable."""
    update_topic = notifications.TOPIC_CATEGORIES
    ordering = twl.Text(sort_default=True)
    category_id = twl.Text(id='id')
    naming_convention = twl.Text()
    actions = twl.Box(
        children=[
            twl.Button(id='edit',
                action=url('/category/%(id)s/edit'),
                dialog=True,
                children=[
                    twl.Icon(id='edit',
                        icon_class='icon_edit',
                        help_text='edit'),
            ]),
            twl.Button(id='delete',
                action=url('/category/%(id)s/delete'),
                dialog=True,
                children=[
                    twl.Icon(id='delete',
                        icon_class='icon_delete',
                        help_text='delete'),
            ]),
    ])


class TableProjectsActive(twl.LiveTable):
    """Active projects livetable."""
    update_topic = notifications.TOPIC_PROJECTS_ACTIVE
    update_condition = '!msg.ob.archived || msg.update_type=="archived"'
    update_functions = ('{"added": lw.livetable.addrow,'
                        ' "deleted": lw.livetable.deleterow,'
                        ' "updated": lw.livetable.updaterow,'
                        ' "archived": lw.livetable.deleterow,'
                        ' "activated": lw.livetable.addrow}')
    show_headers = False

    project_id = twl.Text(id='id')
    name = twl.Text()
    description = twl.Text()
    actions = twl.Box(
        children=[
            twl.Button(id='archive',
                action='%(id)s/archive',
                dialog=True,
                children=[
                    twl.Icon(id='archive',
                        icon_class='icon_archive',
                        help_text='archive'),
            ]),
            twl.Button(id='edit',
                action='%(id)s/edit',
                dialog=True,
                children=[
                    twl.Icon(id='edit',
                        icon_class='icon_edit',
                        help_text='edit'),
            ]),
            twl.Button(id='delete',
                action='%(id)s/delete',
                dialog=True,
                children=[
                    twl.Icon(id='delete',
                        icon_class='icon_delete',
                        help_text='delete'),
            ]),
    ])


class TableProjectsArchived(twl.LiveTable):
    """Archived projects livetable."""
    update_topic = notifications.TOPIC_PROJECTS_ARCHIVED
    update_condition = 'msg.ob.archived || msg.update_type=="activated"'
    update_functions = ('{"added": lw.livetable.addrow,'
                        ' "deleted": lw.livetable.deleterow,'
                        ' "updated": lw.livetable.updaterow,'
                        ' "archived": lw.livetable.addrow,'
                        ' "activated": lw.livetable.deleterow}')
    show_headers = False

    project_id = twl.Text(id='id')
    name = twl.Text()
    description = twl.Text()
    actions = twl.Box(
        children=[
            twl.Button(id='activate',
                action='%(id)s/activate',
                dialog=True,
                children=[
                    twl.Icon(id='activate',
                        icon_class='icon_activate',
                        help_text='activate'),
        ]),
    ])


class TableScenes(twl.LiveTable):
    """Scene livetable."""
    update_topic = notifications.TOPIC_SCENES
    show_headers = False
    thumbnail = twl.Box(
        css_class='thumbnail',
        children=[
            twl.Image(id='thumbnail',
                help_text='thumbnail',
                css_class='thumbnail',
                condition='data.has_preview',
                src=url('/repo/%(thumbnail)s')
            )
    ])
    namelink = twl.Link(
        dest=url('/scene/%(proj_id)s/%(name)s/'),
        sort_default=True,
        children=[
            twl.Text(id='name', help_text='name')
    ])
    description = twl.Text()
#    shots = StatusIconBox(
#        dest=url('/shot/%(proj_id)s/%(parent_name)s/%(name)s/'),
#        children=[
#            StatusIcon(help_text='')
#    ])
    actions = twl.Box(
        condition='$.inArray(data.user_id, data.project.admin_ids)>=0',
        children=[
            twl.Button(id='edit',
                action=url('/scene/%(proj_id)s/%(name)s/edit'),
                dialog=True,
                children=[
                    twl.Icon(id='edit',
                        icon_class='icon_edit',
                        help_text='edit'),
            ]),
            twl.Button(id='delete',
                action=url('/scene/%(proj_id)s/%(name)s/delete'),
                dialog=True,
                children=[
                    twl.Icon(id='delete',
                        icon_class='icon_delete',
                        help_text='delete'),
            ]),
    ])


class TableShots(twl.LiveTable):
    """Shot livetable."""
    update_topic = notifications.TOPIC_SHOTS
    show_headers = False
    thumbnail = twl.Box(
        css_class='thumbnail',
        children=[
            twl.Image(id='thumbnail',
                help_text='thumbnail',
                css_class='thumbnail',
                condition='data.has_preview',
                src=url('/repo/%(thumbnail)s')
            ),
    ])
    namelink = twl.Link(
        dest=url('/shot/%(proj_id)s/%(parent_name)s/%(name)s/'),
        sort_default=True,
        children=[
            twl.Text(id='name', help_text='name')
    ])
    description = twl.Text()
    frames = twl.Text()
    categories = twl.Box(
        css_class='statusiconbox',
        children=[
            twl.Link(
                dest='%s#%s' % (
                      url('/shot/%(proj_id)s/%(parent_name)s/%(name)s'),
                      url('/asset/%(proj_id)s/%(container_type)s/%(id)s')),
                children=[
#                    StatusIcon(id='item_status',
#                        help_text='%(item_name)s: %(item_status)s'),
            ])
    ])
    actions = twl.Box(
        condition='$.inArray(data.user_id, data.project.admin_ids)>=0',
        children=[
            twl.Button(id='edit',
                action=url('/shot/%(proj_id)s/%(parent_name)s/%(name)s/edit'),
                dialog=True,
                children=[
                    twl.Icon(id='edit',
                        icon_class='icon_edit',
                        help_text='edit'),
            ]),
            twl.Button(id='delete',
                action=url('/shot/%(proj_id)s/%(parent_name)s/%(name)s/delete'),
                dialog=True,
                children=[
                    twl.Icon(id='delete',
                        icon_class='icon_delete',
                        help_text='delete'),
            ]),
    ])


class TableLibgroups(twl.LiveTable):
    """Libgroup livetable."""
    parent_id = twc.Param('Libgroup parent id', default=None)
    update_topic = notifications.TOPIC_LIBGROUPS
    show_headers = False
    thumbnail = twl.Box(
        css_class='thumbnail',
        children=[
            twl.Image(
                help_text='thumbnail',
                css_class='thumbnail',
                condition='data.has_preview',
                src=url('/repo/%(thumbnail)s'))
    ])
    namelink = twl.Link(
        dest=url('/libgroup/%(proj_id)s/%(id)s/'),
        sort_default=True,
        children=[
            twl.Text(id='name',
                help_text='name')
    ])
    description = twl.Text()
#    subgroups = StatusIconBox(
#        dest=url('/libgroup/%(proj_id)s/%(id)s'),
#        children=[
#          StatusIcon(help_text='')
#    ])
    categories = twl.Box(
        css_class='statusiconbox',
        children=[
            twl.Link(
                dest='%s#%s' % (
                      url('/libgroup/%(proj_id)s/%(id)s'),
                      url('/asset/%(proj_id)s/%(container_type)s/%(id)s')),
                children=[
#                    StatusIcon(id='item_status',
#                        help_text='%(item_name)s: %(item_status)s')
            ])
    ])
    actions = twl.Box(
        condition='$.inArray(data.user_id, data.project.admin_ids)>=0',
        children=[
            twl.Button(id='edit',
                action=url('/libgroup/%(proj_id)s/%(id)s/edit'),
                dialog=True,
                children=[
                    twl.Icon(id='edit',
                        icon_class='icon_edit',
                        help_text='edit'),
            ]),
            twl.Button(id='delete',
                action=url('/libgroup/%(proj_id)s/%(id)s/delete'),
                dialog=True,
                children=[
                    twl.Icon(id='delete',
                        icon_class='icon_delete',
                        help_text='delete'),
            ]),
    ])
    
    def prepare(self):
        super(TableLibgroups, self).prepare()
        self.update_condition = 'msg.ob.parent_id==%s' % (
                        self.parent_id and '"%s"' % self.parent_id or 'null')


class TableAssets(twl.LiveTable):
    """Asset livetable."""
    category = twc.Param('Asset category', default='')
    
    update_topic = notifications.TOPIC_ASSETS
    show_headers = False
    thumbnail = twl.Box(
        css_class='thumbnail status %(status)s',
        children=[
            twl.Link(
                dest=url('/repo/%(proj_id)s/preview.png'),
                condition='data.has_preview',
                children=[
                    twl.Image(
                        help_text='preview',
                        css_class='thumbnail',
                        src=url('/repo/%(thumbnail)s'))
            ])
    ])
    name = twl.Box(
        css_class='status %(status)s',
        children=[
            twl.Text(id='name', sort_default=True),
            twl.Text(id='owner_id',
                css_class='owner',
                condition='data.checkedout',
                text='%s: %s' % ('checkedout by', '%(owner_user_name)s'),
                help_text='%(owner_id)s (%(owner_display_name)s)',
            )
    ])
    current_fmtver = twl.Text(
        css_class='status %(status)s',
        help_text='version')
#    status = StatusIcon(
#        css_class='status %(status)s',
#        icon_class='asset',
#        help_text='status: ')
    note = twl.Box(
        css_class='status %(status)s',
        children=[
            twl.Text(id='current_header',
                css_class='note_header',
                help_text='latest comment'),
            twl.Text(id='current_summary',
                help_text='latest comment'),
    ])
    actions = twl.Box(
        css_class='status %(status)s',
        children=[
            twl.Button(id='history',
                action=url('/asset/%(proj_id)s/%(id)s'),
                dialog=True,
                children=[
                    twl.Icon(id='history',
                        icon_class='icon_history',
                        help_text='asset history'),
            ]),
            twl.Button(id='addnote',
                action=url('/note/%(proj_id)s/%(current_id)s/new'),
                icon_class='icon_edit',
                help_text='add note',
                dialog=True,
                children=[
                    twl.Icon(id='addnote',
                        icon_class='icon_edit',
                        help_text='add note'),
            ]),
            twl.Button(id='checkout',
                condition=('!data.checkedout && !data.approved '
                    '&& ($.inArray(data.user_id, data.supervisor_ids)>=0 '
                    '|| $.inArray(data.user_id, data.artist_ids)>=0)'),
                action=url('/asset/%(proj_id)s/%(id)s/checkout'),
                children=[
                    twl.Icon(id='checkout',
                        icon_class='icon_checkout',
                        help_text='checkout'),
            ]),
            twl.Button(id='release',
                condition=('data.checkedout && !data.submitted && '
                    '&& !data.approved && (data.user_id==data.owner_id '
                    '|| $.inArray(data.user_id, data.supervisor_ids)>=0)'),
                action=url('/asset/%(proj_id)s/%(id)s/release'),
                children=[
                    twl.Icon(id='release',
                        icon_class='icon_release',
                        help_text='release'),
            ]),
            twl.Button(id='publish',
                condition=('data.checkedout '
                    '&& data.user_id==data.owner_id'),
                action=url('/asset/%(proj_id)s/%(id)s/publish'),
                dialog=True,
                children=[
                    twl.Icon(id='publish',
                        icon_class='icon_publish',
                        help_text='publish a new version'),
            ]),
            twl.Button(id='submit', icon_class='submit',
                condition=('data.checkedout && data.current_ver>0 '
                    '&& !data.submitted && !data.approved '
                    '&& data.user_id==data.owner_id'),
                action=url('/asset/%(proj_id)s/%(id)s/submit'),
                dialog=True,
                children=[
                    twl.Icon(id='submit',
                        icon_class='icon_submit',
                        help_text='submit for approval'),
            ]),
            twl.Button(id='recall',
                condition=('data.submitted && !data.approved '
                    '&& data.user_id==data.owner_id'),
                action=url('/asset/%(proj_id)s/%(id)s/recall'),
                dialog=True,
                children=[
                    twl.Icon(id='recall',
                        icon_class='icon_recall',
                        help_text='recall submission'),
            ]),
            twl.Button(id='sendback',
                condition=('data.submitted && !data.approved '
                    '&& $.inArray(data.user_id, data.supervisor_ids)>=0'),
                action=url('/asset/%(proj_id)s/%(id)s/sendback'),
                dialog=True,
                children=[
                    twl.Icon(id='sendback',
                        icon_class='icon_sendback',
                        help_text='send back for revisions'),
            ]),
            twl.Button(id='approve',
                condition=('data.submitted && !data.approved '
                    '&& $.inArray(data.user_id, data.supervisor_ids)>=0'),
                action=url('/asset/%(proj_id)s/%(id)s/approve'),
                dialog=True,
                children=[
                    twl.Icon(id='approve',
                        icon_class='icon_approve',
                        help_text='approve'),
            ]),
            twl.Button(id='revoke',
                condition=('data.approved '
                    '&& $.inArray(data.user_id, data.supervisor_ids)>=0'),
                action=url('/asset/%(proj_id)s/%(id)s/revoke'),
                dialog=True,
                children=[
                    twl.Icon(id='revoke',
                        icon_class='icon_revoke',
                        help_text='revoke approval'),
            ]),
            twl.Link(id='download_link',
                condition='data.current_ver && data.current_ver>0',
                dest=url('/asset/%(proj_id)s/%(current_id)s/download'),
                children=[
                    twl.Icon(id='download',
                        icon_class='icon_download',
                        help_text='download',
                    )
            ]),
            twl.Button(id='delete',
                condition='$.inArray(data.user_id, data.project.admin_ids)>=0',
                action=url('/asset/%(proj_id)s/%(id)s/delete'),
                dialog=True,
                children=[
                    twl.Icon(id='delete',
                        icon_class='icon_delete',
                        help_text='delete'),
            ]),
    ])
    
    def prepare(self):
        super(TableAssets, self).prepare()
        self.update_condition = 'msg.ob.category.id=="%s"' % self.category


class TableAssetHistory(twl.LiveTable):
    """Asset history livetable."""
    show_headers = False
    thumbnail = twl.Box(
        css_class='thumbnail',
        children=[
            twl.Link(
#                dest=url('/repo/%(preview_path)s'),
                condition='data.has_preview',
                children=[
                    twl.Image(
                        help_text='preview',
                        css_class='thumbnail',
                        src=url('/repo/%(thumbnail)s'))
            ])
    ])
    fmtver = twl.Text(help_text='ver')
    note = twl.Box(
        children=[
            twl.Text(id='header',
                css_class='note_header',
                help_text=''),
            twl.Box(id='lines',
                children=[
                    twl.Text(id='item_line',
                        help_text='')
            ]),
    ])
    actions = twl.Box(
        children=[
            twl.Link(id='download_link',
                condition='data.ver && data.ver>0',
                dest=url('/asset/%(proj_id)s/%(id)s/download'),
            children=[
                twl.Icon(id='download',
                    icon_class='icon_download',
                    help_text='download',
                )
            ]),
    ])


class TableJournal(twl.LiveTable):
    """Journal entries livetable."""
    curpage = twc.Param('Current displayed page', default='')
    update_topic = notifications.TOPIC_JOURNAL
    show_headers = False
    strftime = twl.Text(
        sort_default=True,
        sort_direction = 'desc',
        help_text='date')
    user_id = twl.Text(help_text='user')
    text = twl.Text()
    
    def prepare(self):
        super(TableJournal, self).prepare()
        self.update_condition = '%s==1' % self.curpage


class TableNotes(twl.LiveTable):
    """Note livetable."""
    update_topic = notifications.TOPIC_NOTES
    show_headers = False
    user_name = twl.Text(
        css_class='note_header',
        help_text='user name')
    strftime = twl.Text(
        sort_default=True,
        sort_direction='desc',
        css_class='note_header',
        help_text='date')
    lines = twl.Box(
        children=[
            twl.Text(id='text', help_text='')
    ])
    actions = twl.Box(
        condition='$.inArray(data.user_id, data.project.admin_ids)>=0',
        children=[
            twl.Button(id='pin',
                condition='!data.sticky',
                action=url('/note/%(proj)s/%(id)s/pin'),
                children=[
                    twl.Icon(id='pin',
                        icon_class='icon_pin',
                        help_text='pin note'),
            ]),
            twl.Button(id='unpin',
                condition='data.sticky',
                action=url('/note/%(proj)s/%(id)s/unpin'),
                children=[
                    twl.Icon(id='unpin',
                        icon_class='icon_unpin',
                        help_text='un-pin note'),
            ]),
            twl.Button(id='delete',
                condition='$.inArray(data.user_id, data.project.admin_ids)>=0',
                action=url('/note/%(proj)s/%(id)s/delete'),
                dialog=True,
                children=[
                    twl.Icon(id='delete',
                        icon_class='icon_delete',
                        help_text='delete'),
            ]),
    ])


############################################################
# Live lists
############################################################
class ListProjects(twl.LiveList):
    """Project livelist."""
    user_id = twc.Param('User id used to filter update messages', default='')
    update_topic = notifications.TOPIC_PROJECTS_ACTIVE

    name = twl.Link(
        dest=url('/project/%(id)s'),
        css_class='%(id)s',
        children=[
            twl.Text(id='name',
                 help_text='%(description)s')
        ])

    def prepare(self):
        super(ListProjects, self).prepare()
        self.update_condition = ('$.inArray("%s", msg.ob.user_ids) > -1' %
                                                                self.user_id)


############################################################
# Live boxes
############################################################
#class BoxTags(LiveBox):
#    """Tag livebox."""
#    params = ['taggable_id']
#    container_class = 'tagbox'
#    update_topic = notifications.TOPIC_TAGS
#    id = Box(children=[
#        Text(id='id', help_text=''),
#        Button(id='remove',
#          condition='$.inArray(data.user_id, data.project.admin_ids)>=0',
#          action=url('/tag/%(taggable_id)s/%(id)s/remove'),
#          children=[Icon(id='remove', icon_class='icon_delete',
#            help_text='remove'),
#        ]),
#        Text(id='separator', help_text='', text=', '),
#    ])
#    
#    def update_params(self, d):
#        super(BoxTags, self).update_params(d)
#        d['update_condition'] = 'msg.taggable_id=="%s"' % d['taggable_id']


#statusbox_js = JSSource(src='''
#    wrap_functions = function(func, box_id, item, show_update, extra_data) {
#        $.each(item.parent.categories, function (i, parent_cat) {
#            if (parent_cat.id==item.category.id)
#                cat = parent_cat;
#        });
#        if (typeof(cat) != 'udefined')
#            func(box_id, cat, show_update, extra_data);
#    }
#    
#    add_categories = function(box_id, item, show_update, extra_data) {
#        if (typeof(item.ordering)!='undefined')   // 'item' is a category
#            lw.livebox.add(box_id, item, show_update, extra_data);
#        else    // 'item' is an asset
#            wrap_functions(lw.livebox.add, box_id, item, false, extra_data);
#    }
#    delete_categories = function(box_id, item, show_update, extra_data) {
#        if (typeof(item.ordering)!='undefined')   // 'item' is a category
#            lw.livebox.delete(box_id, item, show_update, extra_data);
#        else    // 'item' is an asset
#            wrap_functions(lw.livebox.delete, box_id, item, false, extra_data);
#    }
#    update_categories = function(box_id, item, show_update, extra_data) {
#        wrap_functions(lw.livebox.update, box_id, item, false, extra_data);
#    }
#''')


#class BoxScenesStatus(LiveBox):
#    """Scene status livebox."""
#    params = ['proj_id']
#    container_class = 'statusbox'
#    update_topic = notifications.TOPIC_SCENES
#    show_update = False
#    
#    link = Link(dest=url('/scene/%(proj_id)s/%(name)s'),
#        children=[
#          StatusIcon(id='status', help_text='%(name)s: %(status)s')
#    ])
#    
#    def update_params(self, d):
#        super(BoxScenesStatus, self).update_params(d)
#        d['update_condition'] = 'msg.ob.proj_id=="%s"' % d['proj_id']


#class BoxShotsStatus(LiveBox):
#    """Shot status livebox."""
#    params = ['scene_id']
#    container_class = 'statusbox'
#    update_topic = notifications.TOPIC_SHOTS
#    show_update = False
#    
#    link = Link(dest=url('/shot/%(proj_id)s/%(parent_name)s/%(name)s'),
#        children=[
#          StatusIcon(id='status', help_text='%(name)s: %(status)s')
#    ])
#    
#    def update_params(self, d):
#        super(BoxShotsStatus, self).update_params(d)
#        d['update_condition'] = 'msg.ob.parent_id=="%s"' % d['scene_id']


#class BoxLibgroupsStatus(LiveBox):
#    """Libgroup status livebox."""
#    params = ['libgroup_id']
#    container_class = 'statusbox'
#    update_topic = notifications.TOPIC_LIBGROUPS
#    show_update = False
#    
#    link = Link(dest=url('/libgroup/%(proj_id)s/%(id)s'),
#        children=[
#          StatusIcon(id='status', help_text='%(name)s: %(status)s')
#    ])
#    
#    def update_params(self, d):
#        super(BoxLibgroupsStatus, self).update_params(d)
#        libgroup_id = d['libgroup_id'] and '"%s"' % d['libgroup_id'] or 'null'
#        d['update_condition'] = 'msg.ob.parent_id==%s' % libgroup_id


#class BoxCategoriesStatus(LiveBox):
#    """Asset categories status livebox."""
#    params = ['container_id']
#    javascript = [statusbox_js]
#    container_class = 'statusbox'
#    update_topic = notifications.TOPIC_ASSETS
#    update_functions = ('{"added": add_categories,'
#                        ' "deleted": delete_categories,'
#                        ' "updated": update_categories}')
#    show_update = False
#    
#    category = Link(
#          dest='#/asset/%(proj_id)s/%(container_type)s/%(container_id)s',
#          children=[
#            StatusIcon(id='status', help_text='%(name)s: %(status)s')
#    ])
#    
#    def update_params(self, d):
#        super(BoxCategoriesStatus, self).update_params(d)
#        d['update_condition'] = 'msg.ob.parent_id=="%s"' % d['container_id']


#class BoxStatus(LiveBox):
#    """Category status livebox."""
#    params = ['container_id', 'category_id']
#    javascript = [statusbox_js]
#    container_class = 'statusbox'
#    update_topic = notifications.TOPIC_ASSETS
#    update_functions = ('{"added": add_categories,'
#                        ' "deleted": delete_categories,'
#                        ' "updated": update_categories}')
#    show_update = False
#    
#    status = StatusIcon(help_text='%(name)s: %(status)s')
#    
#    def update_params(self, d):
#        super(BoxStatus, self).update_params(d)
#        d['update_condition'] = ('msg.ob.parent_id=="%s" && '
#            'msg.ob.category.id=="%s"' % (d['container_id'], d['category_id']))


############################################################
# Form widgets
############################################################

# defaults for input children
SEL_SIZE = 10
TEXT_AREA_COLS = 30
TEXT_AREA_ROWS = 3
MAX_UPLOAD_FILES = None

# base classes
class SubmitWithFeedback(twf.SubmitButton):
    """A submit button with a loading icon"""
    template = 'mako:spam.templates.forms.submit_feedback'


class RestForm(twf.TableForm):
    """Base class for forms that submit data to a custom REST method via the
    ``_method`` parameter
    """
    custom_method = twc.Param('The custom REST method to use for submitting '
        'the form', default='POST')
    custom_method_field = twf.IgnoredField(name='_method')
    submit = SubmitWithFeedback(id='submit', value='Submit')

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
   
class FormUserNewPassword(RestForm):
    """Change User Password."""
    custom_method = 'NEW_PASSWORD'
    new_password = twf.PasswordField(validator=StringLength(max=80, required=True))
    retype_password = twf.PasswordField(validator=MatchValidator("new_password", required=True))


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
class FormSceneNew(RestForm):
    """New scene form."""
    proj = twf.HiddenField()
    project_name_ = twf.LabelField()
    sc = twf.TextField(label='name', validator=twc.All(StringLength(max=15),
                    twc.RegexValidator(regex=G.pattern_name), required=True))
    description = twf.TextArea(cols=TEXT_AREA_COLS, rows=TEXT_AREA_ROWS)


class FormSceneEdit(RestForm):
    """Edit scene form."""
    custom_method = 'PUT'
    proj = twf.HiddenField()
    sc = twf.HiddenField()
    project_name_ = twf.LabelField()
    scene_name_ = twf.LabelField(label='Name')
    description = twf.TextArea(cols=TEXT_AREA_COLS, rows=TEXT_AREA_ROWS)


class FormSceneConfirm(RestForm):
    """Generic scene confirmation form."""
    proj = twf.HiddenField()
    sc = twf.HiddenField()
    project_name_ = twf.LabelField()
    scene_name_ = twf.LabelField(label='Name')
    description_ = twf.LabelField()


# Shot
class FormShotNew(RestForm):
    """New shot form."""
    proj = twf.HiddenField()
    sc = twf.HiddenField()
    project_name_ = twf.LabelField()
    scene_name_ = twf.LabelField()
    sh = twf.TextField(label='Name', validator=twc.All(StringLength(max=15),
                    twc.RegexValidator(regex=G.pattern_name), required=True))
    description = twf.TextArea(cols=TEXT_AREA_COLS, rows=TEXT_AREA_ROWS)
    action = twf.TextArea(cols=TEXT_AREA_COLS, rows=TEXT_AREA_ROWS)
    frames = twf.TextField(validator=twc.IntValidator)
    handle_in = twf.TextField(validator=twc.IntValidator)
    handle_out = twf.TextField(validator=twc.IntValidator)


class FormShotEdit(RestForm):
    """Edit shot form."""
    custom_method = 'PUT'
    proj = twf.HiddenField()
    sc = twf.HiddenField()
    sh = twf.HiddenField()
    project_name_ = twf.LabelField()
    scene_name_ = twf.LabelField()
    shot_name_ = twf.LabelField(label='Name')
    description = twf.TextArea(cols=TEXT_AREA_COLS, rows=TEXT_AREA_ROWS)
    action = twf.TextArea(cols=TEXT_AREA_COLS, rows=TEXT_AREA_ROWS)
    frames = twf.TextField(validator=twc.IntValidator)
    handle_in = twf.TextField(validator=twc.IntValidator)
    handle_out = twf.TextField(validator=twc.IntValidator)


class FormShotConfirm(RestForm):
    """Generic shot confirmation form."""
    proj = twf.HiddenField()
    sc = twf.HiddenField()
    sh = twf.HiddenField()
    project_name_ = twf.LabelField()
    scene_name_ = twf.LabelField()
    shot_name_ = twf.LabelField(label='Name')
    description_ = twf.LabelField()


# Libgroups
class FormLibgroupNew(RestForm):
    """New libgroup form."""
    proj = twf.HiddenField()
    parent_id = twf.HiddenField()
    project_name_ = twf.LabelField()
    parent_ = twf.LabelField()
    name = twf.TextField(validator=twc.All(StringLength(max=15),
                    twc.RegexValidator(regex=G.pattern_name), required=True))
    description = twf.TextArea(cols=TEXT_AREA_COLS, rows=TEXT_AREA_ROWS)


class FormLibgroupEdit(RestForm):
    """Edit libgroup form."""
    custom_method = 'PUT'
    proj = twf.HiddenField()
    libgroup_id = twf.HiddenField()
    project_name_ = twf.LabelField()
    libgroup_name_ = twf.LabelField(label='Name')
    description = twf.TextArea(cols=TEXT_AREA_COLS, rows=TEXT_AREA_ROWS)


class FormLibgroupConfirm(RestForm):
    """Generic libgroup confirmation form."""
    proj = twf.HiddenField()
    libgroup_id = twf.HiddenField()
    project_name_ = twf.LabelField()
    libgroup_name_ = twf.LabelField(label='Name')
    description_ = twf.LabelField()


# Asset
class FormAssetNew(RestForm):
    """New asset form."""
    proj = twf.HiddenField()
    container_type = twf.HiddenField()
    container_id = twf.HiddenField()
    project_name = twf.LabelField()
    category_id = twf.SingleSelectField(label='category', options=[],
            validator=twc.All(twc.RegexValidator(regex=G.pattern_name),
                                    StringLength(max=30), required=True),
            default='')
    name = twf.TextField(validator=twc.All(
                        twc.Any(twc.RegexValidator(regex=G.pattern_file),
                                twc.RegexValidator(regex=G.pattern_seq)),
                        CategoryNamingConvention(category_field='category_id'),
                        required=True))
    comment = twf.TextArea(cols=TEXT_AREA_COLS, rows=TEXT_AREA_ROWS)


class FormAssetEdit(RestForm):
    """Edit asset form."""
    custom_method = 'PUT'
    proj = twf.HiddenField()
    project_name_ = twf.LabelField()


class FormAssetConfirm(RestForm):
    """Generic asset confirmation form."""
    proj = twf.HiddenField()
    asset_id = twf.HiddenField()
    project_name_ = twf.LabelField()
    container_ = twf.LabelField()
    category_id_ = twf.LabelField()
    asset_name_ = twf.LabelField(label='Name')


class Upload(twf.FormField):
    """Advanced upload field for the publish asset form.
    
    An ``Upload`` field uploads file to the server as they are selected
    (or dragged onto it) and shows a progress bar for the upload."""
    target = twc.Param('Url of the controller that will receive the files',
        default=url('/upload'))
    queue = twc.Param('DOM id of the upload queue element',
        default='#upload_queue')
    submitter = twc.Param('DOM class of the submit button. It will be used to'
        'disable the button while uploading files', default='.submitbutton')
    ext = twc.Param('Restrict uploading to files with this extension. Use None'
        'to allow all files', default=None)

    template = 'mako:spam.templates.widgets.upload'
    upload_js = twc.JSLink(link=url('/js/widgets/upload.js'))
    resources = [upload_js]
    


class FormAssetPublish(RestForm):
    """Publish asset form."""
    custom_method = 'PUBLISH'
    proj = twf.HiddenField()
    asset_id = twf.HiddenField()
    uploaded = twf.HiddenField(validator=twc.ListLengthValidator(
                    min=1, max=MAX_UPLOAD_FILES,
                    msgs={'tooshort': ('list_tooshort',
                                       'Please choose the file(s) to upload'),
                          'toolong': ('list_toolong',
                                      'Too many files selected'),
                         },
                    required=True))
    uploader = Upload(label='File(s) to Upload')
    spacer = twf.Spacer()
    comment = twf.TextArea(cols=TEXT_AREA_COLS, rows=TEXT_AREA_ROWS)


class FormAssetStatus(RestForm):
    """Asset status form."""
    proj = twf.HiddenField()
    asset_id = twf.HiddenField()
    project_name_ = twf.LabelField()
    container_ = twf.LabelField()
    category_id_ = twf.LabelField()
    asset_name_ = twf.LabelField(label='Name')
    comment = twf.TextArea(cols=TEXT_AREA_COLS, rows=TEXT_AREA_ROWS)

