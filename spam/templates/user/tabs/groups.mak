<%inherit file="spam.templates.tab"/>

% for group in groups:
    <div id="${'toggle_%s' % group.group_name}" class="toggle">
        <div class="toggle_header title">
            <span class="toggle_arrow"/>
            <h2 class="toggle_title">${group.group_name}</h2>
        </div>
        <div class="toggleable">
            <a href="${tg.url('/user/%s/add_to_group' % group.group_name)}"
               rel="#overlay" class="overlay button">add to group</a>
            <br/>
            <br/>
            ${c.t_group_users(id='users_%s' % group.group_name,
                              extra_data=dict(group_name=group.group_name),
                              items=list(group.users)) | n}
        </div>
    </div>
% endfor

