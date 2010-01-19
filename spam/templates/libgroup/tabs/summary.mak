<%inherit file="spam.templates.tab"/>

Summary tab for libgroup ${c.libgroup.path}
<br/>
<br/>

<h2>tags</h2>
<a href="${tg.url('/tag/%s/new' % c.libgroup.id)}"
   rel="#overlay" class="overlay button">add tag</a>
${c.l_tags(id="taglist", items=c.libgroup.tags) | n}
<br/>
<br/>

<h2>notes</h2>
<a href="${tg.url('/note/%s/new' % c.libgroup.id)}"
   rel="#overlay" class="overlay button">add note</a>
${c.t_notes(id="notestable", items=c.libgroup.notes) | n}

