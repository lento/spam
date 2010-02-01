<%inherit file="spam.templates.tab"/>

% if c.predicates.is_project_admin():
<a href="${tg.url('/scene/%s/new' % c.project.id)}" rel="#overlay" class="overlay button">new scene</a>
<br/>
<br/>
% endif

${c.t_scenes(items=scenes, update_listener_adder="notify.add_listener_tab",
             extra_data=extra_data) | n}

