<%inherit file="spam.templates.tab"/>

Summary tab for scene ${c.scene.path}
<br/>
<br/>

<h2>tags</h2>
<a href="${tg.url('/tag/%s/new' % c.scene.id)}"
   rel="#overlay" class="overlay button">add tag</a>
${c.l_tags(id="taglist", items=c.scene.tags) | n}
<br/>
<br/>

<h2>notes</h2>
<a href="${tg.url('/note/%s/new' % c.scene.id)}"
   rel="#overlay" class="overlay button">add note</a>
${c.t_notes(id="notestable", items=c.scene.notes,
                                    annotable_id=c.scene.annotable.id) | n}

