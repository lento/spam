<%def name="user()">
    % if tg.predicates.not_anonymous():
        <div id="sb_user" class="sidebar">
            <div class="title">${_('user')}</div>
            <ul class="links">
                <li class="home"><a href="${tg.url('/user/home')}">${_('home')}</a></li>
            </ul>
        </div>
    % endif
</%def>    

<%def name="admin()">
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
                        <li class="projects"><a href="${tg.url('/admin/projects/')}">${_('projects')}</a></li>
                    </ul>
                </div>
            </div>
        </div>
    % endif
</%def>    

<%def name="projects()">
    % if tg.predicates.not_anonymous():
        <div id="sb_projects" class="sidebar">
            <div class="title">${_('projects')}</div>
            <ul class="links">
                % for p in c.user.projects:
                    <li class="${p.id}">
                        <div class="hidden id">${p.id}</div>
                        <a href="${tg.url('/project/%s' % p.id)}">${p.name}</a>
                    </li>
                % endfor
            </ul>
        </div>
    % endif
</%def>    


