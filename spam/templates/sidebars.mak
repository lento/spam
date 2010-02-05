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

<%def name="sb_user()">
    % if tg.predicates.not_anonymous():
        <div id="sb_user" class="sidebar">
            <div id="sb_user_toggle" class="toggle">
                <div class="toggle_header title">
                    <span class="toggle_arrow"/>
                    <span class="toggle_title">${_('user')}</span>
                </div>
                <div class="toggleable">
                    <ul class="links">
                        <li class="home"><a href="${tg.url('/user/home')}">${_('home')}</a></li>
                    </ul>
                </div>
            </div>
        </div>
    % endif
</%def>    

<%def name="sb_admin()">
    % if tg.predicates.in_group('administrators'):
        <div id="sb_admin" class="sidebar">
            <div id="sb_admin_toggle" class="toggle">
                <div class="toggle_header title">
                    <span class="toggle_arrow"/>
                    <span class="toggle_title">${_('admin')}</span>
                </div>
                <div class="toggleable">
                    <ul class="links">
                        <li class="users"><a href="${tg.url('/user/')}">${_('users')}</a></li>
                        <li class="categories"><a href="${tg.url('/category/')}">${_('categories')}</a></li>
                        <li class="projects"><a href="${tg.url('/project/')}">${_('projects')}</a></li>
                        <li class="journal"><a href="${tg.url('/journal')}">${_('journal')}</a></li>
                    </ul>
                </div>
            </div>
        </div>
    % endif
</%def>    

<%def name="sb_projects()">
    % if tg.predicates.not_anonymous():
        <div id="sb_projects" class="sidebar">
            <div id="sb_projects_toggle" class="toggle">
                <div class="toggle_header title">
                    <span class="toggle_arrow"/>
                    <span class="toggle_title">${_('projects')}</span>
                </div>
                <div class="toggleable">
                    ${c.l_projects(id='projectslist', items=list(c.user.projects),
                                                    user_id=c.user.user_id) | n}
                </div>
            </div>
        </div>
    % endif
</%def>    

<%def name="sb_project()">
    % if tg.predicates.not_anonymous() and c.project:
        ${c.j_notify_client()}
        <div id="sb_project" class="sidebar">
            <div class="title">
                <a href="${tg.url('/project/%s' % c.project.id)}">${c.project.name}</a>
                <div class="icon"></div>
            </div>
            <div id="sb_project_content"></div>
        </div>
        <script type="text/javascript">
            $(function() {
                $("#sb_project").addClass("loading");
                $("#sb_project_content").load("${tg.url('/project/%s/sidebar' % c.project.id)}", function() {
                    notify.add_listener("/topic/projects", function(msg) {
                        console.log("#sb_project listener", msg)
                        if (msg.ob.id=="${c.project.id}" && msg.update_type=="updated") {
                            $("#sb_project").load("${tg.url('/project/%s/sidebar' % c.project.id)}");
                        }
                    });
                    $("#sb_project").removeClass("loading");
                });
            });
        </script>
    % endif
</%def>

