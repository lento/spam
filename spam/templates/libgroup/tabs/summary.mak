## SPAM Spark Project & Asset Manager
##
## This program is free software; you can redistribute it and/or
## modify it under the terms of the GNU Lesser General Public
## License as published by the Free Software Foundation; either
## version 3 of the License, or (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
## Lesser General Public License for more details.
##
## You should have received a copy of the GNU Lesser General Public
## License along with this program; if not, write to the
## Free Software Foundation, Inc., 59 Temple Place - Suite 330,
## Boston, MA 02111-1307, USA.
##
## Original Copyright (c) 2010, Lorenzo Pierfederici <lpierfederici@gmail.com>
## Contributor(s): 
##

<%inherit file="spam.templates.tab"/>

% if c.libgroup.subgroups:
    <h2>${_('subgroups')}</h2>
    ${c.b_libgroups_status(id="status_%s_subgroups" % c.libgroup.id,
                    items=c.libgroup.subgroups, libgroup_id=c.libgroup.id,
                    update_listener_adder="notify.add_listener_tab") | n}
    <br/>
    <br/>
% endif

% if c.libgroup.assets:
    <h2>${_('assets')}</h2>
    ${c.b_categories_status(id="status_%s_assets" % c.libgroup.id,
                    items=c.libgroup.categories, container_id=c.libgroup.id,
                    extra_data=cat_extra_data,
                    update_listener_adder="notify.add_listener_tab") | n}
    <br/>
    <br/>
% endif

<h2>${_('tags')}</h2>
% if c.predicates.is_project_admin():
<a href="${tg.url('/tag/%s/new' % c.libgroup.id)}"
   rel="#overlay" class="overlay button">add tags</a>
% endif
${c.b_tags(id="taglist", items=c.libgroup.tags,
                    taggable_id=c.libgroup.taggable.id,
                    extra_data=tag_extra_data,
                    update_listener_adder="notify.add_listener_tab") | n}
<br/>
<br/>

<h2>${_('notes')}</h2>
% if c.predicates.is_project_admin():
<a href="${tg.url('/note/%s/new' % c.libgroup.id)}"
   rel="#overlay" class="overlay button">add note</a>
% endif
${c.t_notes(id="notestable", items=c.libgroup.notes,
                    annotable_id=c.libgroup.annotable.id,
                    extra_data=note_extra_data,
                    update_listener_adder="notify.add_listener_tab") | n}

