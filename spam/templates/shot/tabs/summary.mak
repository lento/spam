<%inherit file="spam.templates.tab"/>

<h2>${_('assets')}</h2>
${c.b_categories_status(id="status_%s" % c.shot.id, items=c.shot.categories,
                        container_id=c.shot.id, extra_data=cat_extra_data) | n}
<br/>
<br/>

<h2>${_('tags')}</h2>
<a href="${tg.url('/tag/%s/new' % c.shot.id)}"
   rel="#overlay" class="overlay button">add tag</a>
${c.l_tags(id="taglist", items=c.shot.tags) | n}
<br/>
<br/>

<h2>${_('notes')}</h2>
<a href="${tg.url('/note/%s/new' % c.shot.id)}"
   rel="#overlay" class="overlay button">add note</a>
${c.t_notes(id="notestable", items=c.shot.notes,
                                    annotable_id=c.shot.annotable.id) | n}

