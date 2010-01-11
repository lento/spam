<%inherit file="spam.templates.tab"/>

Summary tab for shot ${c.shot.path}
<br/>
<br/>

<h2>tags</h2>
<a href="${tg.url('/tag/%s/new' % c.shot.id)}"
   rel="#overlay" class="overlay button">add tag</a>
${c.l_tags(id="taglist", items=tags) | n}

