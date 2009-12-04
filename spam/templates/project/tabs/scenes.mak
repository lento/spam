<%inherit file="spam.templates.tab"/>

<a href="${tg.url('/scene/%s/new' % c.project.id)}" rel="#overlay" class="overlay button">new scene</a>
<br/>
<br/>
${c.t_scenes(items=scenes, update_listener_adder="notify.add_listener_tab") | n}

