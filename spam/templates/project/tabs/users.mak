<%inherit file="spam.templates.tab"/>

<div id="toggle_admins" class="toggle">
    <div class="toggle_header title">
        <span class="toggle_arrow"/>
        <h1 class="toggle_title">${_('administrators')}</h1>
    </div>
    <div class="toggleable">
        <a href="${tg.url('/user/%s/add_admins' % c.project.id)}"
           rel="#overlay" class="overlay button">add</a>
        ${c.t_project_admins(id='users_%s' % c.project.id,
                          extra_data=dict(proj=c.project.id),
                          items=list(c.project.admins)) | n}
    </div>
</div>

<div id="toggle_supervisors" class="toggle">
    <div class="toggle_header title">
        <span class="toggle_arrow"/>
        <h1 class="toggle_title">${_('supervisors')}</h1>
    </div>
    <div class="toggleable">
        ##${c.t_group_users(id='users_%s' % group.group_name,
        ##                  extra_data=dict(group_name=group.group_name),
        ##                  items=list(group.users)) | n}
        % for cat in categories:
            <div id="${'toggle_supervisors_%s' % cat.name}" class="toggle">
                <div class="toggle_header title">
                    <span class="toggle_arrow"/>
                    <h2 class="toggle_title">${cat.name}</h2>
                </div>
                <div class="toggleable">
                    <a href="${tg.url('/user/%s/%s/add_supervisors' % (c.project.id, cat.name))}"
                       rel="#overlay" class="overlay button">add</a>
                    <br/>
                    <br/>
                                
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
        ##${c.t_group_users(id='users_%s' % group.group_name,
        ##                  extra_data=dict(group_name=group.group_name),
        ##                  items=list(group.users)) | n}
        % for cat in categories:
            <div id="${'toggle_artists_%s' % cat.name}" class="toggle">
                <div class="toggle_header title">
                    <span class="toggle_arrow"/>
                    <h2 class="toggle_title">${cat.name}</h2>
                </div>
                <div class="toggleable">
                    <a href="${tg.url('/user/%s/%s/add_artists' % (c.project.id, cat.name))}"
                       rel="#overlay" class="overlay button">add</a>
                    <br/>
                    <br/>
                    
                </div>
            </div>
        % endfor
    </div>
</div>

