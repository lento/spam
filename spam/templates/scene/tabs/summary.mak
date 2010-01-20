<%inherit file="spam.templates.tab"/>

<h2>${_('shots')}</h2>
${c.b_shots_status(id="status_%s" % (c.scene.id), items=c.scene.shots) | n}
<br/>
<br/>

<h2>${_('tags')}</h2>
<a href="${tg.url('/tag/%s/new' % c.scene.id)}"
   rel="#overlay" class="overlay button">add tag</a>
${c.l_tags(id="taglist", items=c.scene.tags) | n}
<br/>
<br/>

<h2>${_('notes')}</h2>
<a href="${tg.url('/note/%s/new' % c.scene.id)}"
   rel="#overlay" class="overlay button">add note</a>
${c.t_notes(id="notestable", items=c.scene.notes,
                                    annotable_id=c.scene.annotable.id) | n}

