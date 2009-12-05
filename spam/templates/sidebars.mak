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
                    notify.add_listener("/topic/projects", function(data) {
                        console.log("#sb_project listener", data)
                        if (data.ob.id=="${c.project.id}" && data.update_type=="updated") {
                            $("#sb_project").load("${tg.url('/project/%s/sidebar' % c.project.id)}");
                        }
                    });
                    $("#sb_project").removeClass("loading");
                });
            });
        </script>
    % endif
</%def>

