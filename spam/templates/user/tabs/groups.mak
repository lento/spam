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

% for group in groups:
    <div id="${'toggle_%s' % group.group_name}" class="toggle">
        <div class="toggle_header title">
            <span class="toggle_arrow"/>
            <h2 class="toggle_title">${group.group_name}</h2>
        </div>
        <div class="toggleable">
            <a href="${tg.url('/user/%s/add_to_group' % group.group_name)}"
               class="button dialog">add to group</a>
            <br/>
            <br/>
            ${c.t_group_users(id='users_%s' % group.group_name,
                      value=list(group.users),
                      extra_data=dict(group_name=group.group_name),
                      update_filter=group.group_name,
                  ).display() | n}
        </div>
    </div>
% endfor

