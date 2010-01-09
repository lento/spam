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
        % for cat in categories:
            <div id="${'toggle_supervisors_%s' % cat.id}" class="toggle">
                <div class="toggle_header title">
                    <span class="toggle_arrow"/>
                    <h2 class="toggle_title">${cat.id}</h2>
                </div>
                <div class="toggleable">
                    <a href="${tg.url('/user/%s/%s/add_supervisors' % (c.project.id, cat.id))}"
                       rel="#overlay" class="overlay button">add</a>
                    ${c.t_project_supervisors(id='supervisors_%s_%s' % (c.project.id, cat.id),
                                      extra_data=dict(proj=c.project.id, cat=cat.id),
                                      items=list(supervisors[cat.id])) | n}
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
                    ${c.t_project_artists(id='artists_%s_%s' % (c.project.id, cat.id),
                                      extra_data=dict(proj=c.project.id, cat=cat.id),
                                      items=list(artists[cat.id])) | n}
                </div>
            </div>
        % endfor
    </div>
</div>

