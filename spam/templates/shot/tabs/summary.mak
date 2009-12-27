<%inherit file="spam.templates.tab"/>

Summary tab for shot ${c.shot.path}
<br/>
<br/>

<h2>tags</h2>
<a href="${tg.url('/shot/%s/%s/%s/add_tag' % (c.project.id, c.shot.parent.name, c.shot.name))}"
   rel="#overlay" class="overlay button">add tag</a>
${c.l_tags(id="taglist", items=tags) | n}

