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
                        <li class="users"><a href="${tg.url('/admin/users')}">${_('users')}</a></li>
                        <li class="groups"><a href="${tg.url('/admin/groups')}">${_('groups')}</a></li>
                        <li class="permissions"><a href="${tg.url('/admin/permissions')}">${_('permissions')}</a></li>
                        <li class="projects"><a href="${tg.url('/project/')}">${_('projects')}</a></li>
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
                    <ul class="links">
                        % for p in c.user.projects:
                        <li class="${p.id}">
                            <div class="hidden id">${p.id}</div>
                            <a href="${tg.url('/project/%s' % p.id)}">${p.name}</a>
                        </li>
                        % endfor
                    </ul>
                </div>
            </div>
        </div>
    % endif
</%def>    

<%def name="insert_libgroup(libgroup)">
    <li>
        <a href="${tg.url('/libgroup/%s/%s' % (project.id, libgroup.name))}">${libgroup.name}</a>
        % if libgroup.subgroups:
            <ul>
                % for subgroup in libgroup.subgroups:
                    ${insert_libgroup(subgroup)}
                % endfor
            </ul>
        % endif
    </li>
</%def>    

<%def name="sb_project()">
    % if tg.predicates.not_anonymous() and project:
        <script type="text/javascript">
        $(function() {
            $("#sb_project_tree").treeview({
                persist: "cookie",
                cookieId: "project_treeview",
                cookieOptions: {path: "${tg.url('/')}"},
                collapsed: true
            });
        });
        </script>
        
        <div id="sb_project" class="sidebar">
            <div class="title">${project.name}</div>
            <ul id="sb_project_tree">
                <li>
                    <span>scenes</span>
                    % if project.scenes:
                        <ul id="sb_project_scenes">
                            % for scene in project.scenes:
                            <li>
                                <a href="${tg.url('/scene/%s/%s' % (project.id, scene.name))}">
                                    ${scene.name}
                                </a>
                                % if scene.shots:
                                    <ul>
                                        % for shot in scene.shots:
                                        <li>
                                            <a href="${tg.url('/shot/%s/%s/%s' % (project.id, scene.name, shot.name))}">
                                                ${shot.name}
                                            </a>
                                        </li>
                                        % endfor
                                    </ul>
                                % endif
                            </li>
                            % endfor
                        </ul>
                    % endif
                </li>
                <li>
                    <span>library</span>
                    % if project.libgroups:
                        <ul id="sb_project_libgroups">
                            % for libgroup in project.libgroups:
                                ${insert_libgroup(libgroup)}
                            % endfor
                        </ul>
                    % endif
                </li>
            </ul>
        </div>
    % endif
</%def>    

<%doc> ## prerendered version of the project treeview... doesn't look faster
<%def name="insert_libgroup(libgroup, last=False)">
    <%
        subgroups = libgroup.subgroups
        lenght = len(subgroups)
        expandable = lenght > 0
        if expandable and last:
            cssclass = 'expandable lastExpandable'
        elif expandable:
            cssclass = 'expandable'
        elif last:
            cssclass = 'last'
        else:
            cssclass = ''
    %>
    <li class="${cssclass}">
        % if expandable:
            <div class="hitarea expandable-hitarea ${last and 'lastExpandable-hitarea' or ''}"/></div>
        % endif
        <a href="${tg.url('/libgroup/%s/%s' % (project.id, libgroup.name))}">${libgroup.name}</a>
        % if subgroups:
            <ul>
                % for i in range(lenght):
                    ${insert_libgroup(subgroups[i], last=(lenght-i == 1))}
                % endfor
            </ul>
        % endif
    </li>
</%def>    

<%def name="sb_project()">
    % if tg.predicates.not_anonymous() and project:
        <script type="text/javascript">
        $(function() {
            $("#sb_project_tree").treeview({
                persist: "cookie",
                prerendered: true
            });
        });
        </script>
        
        <div id="sb_project" class="sidebar">
            <div class="title">${project.name}</div>
            <ul id="sb_project_tree">
                <li class="expandable"><div class="hitarea expandable-hitarea"/></div>
                    <span>scenes</span>
                    <ul id="sb_project_scenes">
                        % for scene in project.scenes:
                        <li class="expandable"><div class="hitarea expandable-hitarea"/></div>
                            <a href="${tg.url('/scene/%s/%s' % (project.id, scene.name))}">${scene.name}</a>
                            <ul>
                                % for shot in scene.shots:
                                <li>
                                    <a href="${tg.url('/shot/%s/%s' % (project.id, shot.name))}">${shot.name}</a>
                                </li>
                                % endfor
                            </ul>
                        </li>
                        % endfor
                    </ul>
                </li>
                <li class="expandable lastExpandable">
                    <div class="hitarea expandable-hitarea lastExpandable-hitarea"/></div>
                    <span>library</span>
                    <ul id="sb_project_libgroups">
                        <% lenght = len(project.libgroups) %>
                        % for i in range(lenght):
                            ${insert_libgroup(project.libgroups[i], last=(lenght-i == 1))}
                        % endfor
                    </ul>
                </li>
            </ul>
        </div>
    % endif
</%def>    
</%doc>


