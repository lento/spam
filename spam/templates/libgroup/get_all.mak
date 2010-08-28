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

<%
    new_url = hasattr(c, 'parent') and hasattr(c.parent, 'id') and '%s/%s' % (c.project.id, c.parent.id) or c.project.id
%>

% if c.predicates.is_project_admin():
<a href="${tg.url('/libgroup/%s/new' % new_url)}" class="button dialog">
    new libgroup
</a>
<br/>
<br/>
% endif

${c.t_libgroups.display() | n}

