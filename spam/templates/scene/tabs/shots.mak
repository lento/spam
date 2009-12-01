<%inherit file="spam.templates.tab"/>

<a href="${tg.url('/shot/%s/%s/new' % (c.project.id, c.scene.name))}" rel="#overlay" class="overlay button">new shot</a>
<br/>
<br/>
${c.t_shots(items=shots) | n}

