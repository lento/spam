<%inherit file="spam.templates.tab"/>

<h2>${_('shots')}</h2>
${c.b_shots_status(id="status_%s" % c.scene.id, items=c.scene.shots,
                    scene_id=c.scene.id,
                    update_listener_adder="notify.add_listener_tab") | n}
<br/>
<br/>

<h2>${_('tags')}</h2>
<a href="${tg.url('/tag/%s/new' % c.scene.id)}"
   rel="#overlay" class="overlay button">add tags</a>
${c.b_tags(id="taglist", items=c.scene.tags,
                    taggable_id=c.scene.taggable.id,
                    extra_data=tag_extra_data,
                    update_listener_adder="notify.add_listener_tab") | n}
<br/>
<br/>

<h2>${_('notes')}</h2>
<a href="${tg.url('/note/%s/new' % c.scene.id)}"
   rel="#overlay" class="overlay button">add note</a>
${c.t_notes(id="notestable", items=c.scene.notes,
                    annotable_id=c.scene.annotable.id,
                    update_listener_adder="notify.add_listener_tab") | n}

