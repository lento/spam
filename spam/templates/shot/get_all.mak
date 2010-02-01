<%inherit file="spam.templates.tab"/>

% if c.predicates.is_project_admin():
<a href="${tg.url('/shot/%s/%s/new' % (c.project.id, c.scene.name))}" rel="#overlay" class="overlay button">new shot</a>
<br/>
<br/>
% endif

${c.t_shots(items=shots,
            update_listener_adder="notify.add_listener_tab",
            extra_data=extra_data) | n}

