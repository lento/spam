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

<div id="toggle_admins" class="toggle">
    <div class="toggle_header title">
        <span class="toggle_arrow"/>
        <h1 class="toggle_title">${_('administrators')}</h1>
    </div>
    <div class="toggleable">
        <a href="${tg.url('/user/%s/add_admins' % c.project.id)}"
           rel="#overlay" class="overlay button">add</a>
        ${c.t_project_admins(id='admins_%s' % c.project.id,
                          extra_data=dict(proj=c.project.id),
                          items=list(c.project.admins),
                          update_listener_adder="notify.add_listener_tab") | n}
    </div>
</div>

<div id="toggle_supervisors" class="toggle">
    <div class="toggle_header title">
        <span class="toggle_arrow"/>
        <h1 class="toggle_title">${_('supervisors')}</h1>
    </div>
    <div class="toggleable">
        % for cat in categories:
            <div id="${'toggle_supervisors_%s' % cat.id}" class="toggle">
                <div class="toggle_header title">
                    <span class="toggle_arrow"/>
                    <h2 class="toggle_title">${cat.id}</h2>
                </div>
                <div class="toggleable">
                    <a href="${tg.url('/user/%s/%s/add_supervisors' % (c.project.id, cat.id))}"
                       rel="#overlay" class="overlay button">add</a>
                    ${c.t_project_supervisors(
                        id='supervisors_%s_%s' % (c.project.id, cat.id),
                        extra_data=dict(proj=c.project.id, cat=cat.id),
                        items=list(supervisors[cat.id]),
                        update_listener_adder="notify.add_listener_tab") | n}
                </div>
            </div>
        % endfor
    </div>
</div>

<div id="toggle_artists" class="toggle">
    <div class="toggle_header title">
        <span class="toggle_arrow"/>
        <h1 class="toggle_title">${_('artists')}</h1>
    </div>
    <div class="toggleable">
        % for cat in categories:
            <div id="${'toggle_artists_%s' % cat.id}" class="toggle">
                <div class="toggle_header title">
                    <span class="toggle_arrow"/>
                    <h2 class="toggle_title">${cat.id}</h2>
                </div>
                <div class="toggleable">
                    <a href="${tg.url('/user/%s/%s/add_artists' % (c.project.id, cat.id))}"
                       rel="#overlay" class="overlay button">add</a>
                    ${c.t_project_artists(
                        id='artists_%s_%s' % (c.project.id, cat.id),
                        extra_data=dict(proj=c.project.id, cat=cat.id),
                        items=list(artists[cat.id]),
                        update_listener_adder="notify.add_listener_tab") | n}
                </div>
            </div>
        % endfor
    </div>
</div>

