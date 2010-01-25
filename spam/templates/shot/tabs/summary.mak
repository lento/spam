<%inherit file="spam.templates.tab"/>

<h2>${_('assets')}</h2>
${c.b_categories_status(id="status_%s" % c.shot.id, items=c.shot.categories,
                    container_id=c.shot.id, extra_data=cat_extra_data,
                    update_listener_adder="notify.add_listener_tab") | n}
<br/>
<br/>

<h2>${_('tags')}</h2>
<a href="${tg.url('/tag/%s/new' % c.shot.id)}"
   rel="#overlay" class="overlay button">add tags</a>
${c.b_tags(id="taglist", items=c.shot.tags,
                    taggable_id=c.shot.taggable.id,
                    extra_data=tag_extra_data,
                    update_listener_adder="notify.add_listener_tab") | n}
<br/>
<br/>

<h2>${_('notes')}</h2>
<a href="${tg.url('/note/%s/new' % c.shot.id)}"
   rel="#overlay" class="overlay button">add note</a>
${c.t_notes(id="notestable", items=c.shot.notes,
                    annotable_id=c.shot.annotable.id,
                    update_listener_adder="notify.add_listener_tab") | n}

