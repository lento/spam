## This file is part of SPAM (Spark Project & Asset Manager).
##
## SPAM is free software: you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
##
## SPAM is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with SPAM.  If not, see <http://www.gnu.org/licenses/>.
##
## Original Copyright (c) 2010, Lorenzo Pierfederici <lpierfederici@gmail.com>
## Contributor(s): 
##

<%inherit file="spam.templates.tab"/>

<h2>${_('assets')}</h2>
##${c.b_categories_status(id="status_%s" % c.shot.id, items=c.shot.categories,
##                    container_id=c.shot.id, extra_data=cat_extra_data,
##                    update_listener_adder="notify.add_listener_tab") | n}
<br/>
<br/>

<h2>${_('tags')}</h2>
% if c.predicates.is_project_admin():
<a href="${tg.url('/tag/%s/new' % c.shot.id)}"
   class="button dialog">add tags</a>
% endif
##${c.b_tags(id="taglist", items=c.shot.tags,
##                    taggable_id=c.shot.taggable.id,
##                    extra_data=tag_extra_data,
##                    update_listener_adder="notify.add_listener_tab") | n}
<br/>
<br/>

<h2>${_('notes')}</h2>
% if c.predicates.is_project_admin():
<a href="${tg.url('/note/%s/%s/new' % (c.project.id, c.shot.id))}"
   rel="#overlay" class="overlay button">add note</a>
% endif
${c.t_notes(id="notestable",
        value=c.shot.notes,
        annotable_id=c.shot.annotable.id,
        extra_data=note_extra_data,
        update_listener_adder="notify.add_listener_tab",
    ).display() | n}

