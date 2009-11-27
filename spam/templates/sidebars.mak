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
                            <a href="${tg.url('/project/%s/' % p.id)}">${p.name}</a>
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
        <a href="${tg.url('/libgroup/%s/%s/' % (c.project.id, libgroup.name))}">${libgroup.name}</a>
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
    % if tg.predicates.not_anonymous() and c.project:
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
            <div class="title">
                <a href="${tg.url('/project/%s' % c.project.id)}">${c.project.name}</a>
            </div>
            <ul id="sb_project_tree">
                <li>
                    <%
                        tab_url = tg.url('/scene/%s' % c.project.id)
                        scenes_url = tg.url('/project/%s/#%s' % (c.project.id, tab_url))
                    %>
                    <a href="${scenes_url}">scenes</a>
                    % if c.project.scenes:
                        <ul id="sb_project_scenes">
                            % for scene in c.project.scenes:
                            <li>
                                <a href="${tg.url('/scene/%s/%s/' % (c.project.id, scene.name))}">
                                    ${scene.name}
                                </a>
                                % if scene.shots:
                                    <ul>
                                        % for shot in scene.shots:
                                        <li>
                                            <a href="${tg.url('/shot/%s/%s/%s/' % (c.project.id, scene.name, shot.name))}">
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
                    % if c.project.libgroups:
                        <ul id="sb_project_libgroups">
                            % for libgroup in c.project.libgroups:
                                ${insert_libgroup(libgroup)}
                            % endfor
                        </ul>
                    % endif
                </li>
            </ul>
        </div>
    % endif
</%def>

