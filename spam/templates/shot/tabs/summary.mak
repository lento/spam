<%inherit file="spam.templates.tab"/>

Summary tab for shot ${c.shot.path}
<br/>
<br/>

<h2>tags</h2>
<a href="${tg.url('/tag/%s/new' % c.shot.id)}"
   rel="#overlay" class="overlay button">add tag</a>
${c.l_tags(id="taglist", items=c.shot.tags) | n}
<br/>
<br/>

<h2>notes</h2>
<a href="${tg.url('/note/%s/new' % c.shot.id)}"
   rel="#overlay" class="overlay button">add note</a>
${c.t_notes(id="notestable", items=c.shot.notes,
                                    annotable_id=c.shot.annotable.id) | n}

