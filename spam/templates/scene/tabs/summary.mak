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

<h2>${_('shots')}</h2>
##${c.b_shots_status(id="status_%s" % c.scene.id, items=c.scene.shots,
##                    scene_id=c.scene.id,
##                    update_listener_adder="notify.add_listener_tab") | n}
<br/>
<br/>

<h2>${_('tags')}</h2>
% if c.predicates.is_project_admin():
<a href="${tg.url('/tag/%s/new' % c.scene.id)}"
   class="button dialog">add tags</a>
% endif
##${c.b_tags(id="taglist", items=c.scene.tags,
##                    taggable_id=c.scene.taggable.id,
##                    extra_data=tag_extra_data,
##                    update_listener_adder="notify.add_listener_tab") | n}
<br/>
<br/>

<h2>${_('notes')}</h2>
% if c.predicates.is_project_admin():
<a href="${tg.url('/note/%s/%s/new' % (c.project.id, c.scene.id))}"
   class="button dialog">add note</a>
% endif
${c.t_notes.display() | n}

