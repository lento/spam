<%inherit file="spam.templates.tab"/>

% if c.libgroup.subgroups:
    <h2>${_('subgroups')}</h2>
    ${c.b_libgroups_status(id="status_%s_subgroups" % c.libgroup.id,
                    items=c.libgroup.subgroups, libgroup_id=c.libgroup.id,
                    update_listener_adder="notify.add_listener_tab") | n}
    <br/>
    <br/>
% endif

% if c.libgroup.assets:
    <h2>${_('assets')}</h2>
    ${c.b_categories_status(id="status_%s_assets" % c.libgroup.id,
                    items=c.libgroup.categories, container_id=c.libgroup.id,
                    extra_data=cat_extra_data,
                    update_listener_adder="notify.add_listener_tab") | n}
    <br/>
    <br/>
% endif

<h2>${_('tags')}</h2>
<a href="${tg.url('/tag/%s/new' % c.libgroup.id)}"
   rel="#overlay" class="overlay button">add tags</a>
${c.b_tags(id="taglist", items=c.libgroup.tags,
                    taggable_id=c.libgroup.taggable.id,
                    extra_data=tag_extra_data,
                    update_listener_adder="notify.add_listener_tab") | n}
<br/>
<br/>

<h2>${_('notes')}</h2>
<a href="${tg.url('/note/%s/new' % c.libgroup.id)}"
   rel="#overlay" class="overlay button">add note</a>
${c.t_notes(id="notestable", items=c.libgroup.notes,
                    annotable_id=c.libgroup.annotable.id,
                    update_listener_adder="notify.add_listener_tab") | n}

