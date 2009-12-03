<%inherit file="spam.templates.tab"/>

<a href="${tg.url('/libgroup/%s/new' % c.project.id)}" rel="#overlay" class="overlay button">new libgroup</a>
<br/>
<br/>
${c.t_libgroups(items=libgroups) | n}

