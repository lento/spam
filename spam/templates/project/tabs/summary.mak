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

<h2>${_('scenes')}</h2>
${c.b_scenes_status(id="status_%s_scenes" % c.project.id,
                    items=c.project.scenes, proj_id=c.project.id,
                    update_listener_adder="notify.add_listener_tab") | n}
<br/>
<br/>

<h2>${_('library')}</h2>
${c.b_libgroups_status(id="status_%s_library" % c.project.id,
                    items=c.project.libgroups, libgroup_id=None,
                    update_listener_adder="notify.add_listener_tab") | n}
<br/>
<br/>

