<%inherit file="spam.templates.tab"/>

% if c.libgroup.subgroups:
    <h2>${_('subgroups')}</h2>
    ${c.b_libgroups_status(id="status_%s_subgroups" % c.libgroup.id,
                                                items=c.libgroup.subgroups) | n}
    <br/>
    <br/>
% endif

% if c.libgroup.assets:
    <h2>${_('assets')}</h2>
    ${c.b_categories_status(id="status_%s_assets" % c.libgroup.id,
                                                items=[c.libgroup]) | n}
    <br/>
    <br/>
% endif

<h2>${_('tags')}</h2>
<a href="${tg.url('/tag/%s/new' % c.libgroup.id)}"
   rel="#overlay" class="overlay button">add tag</a>
${c.l_tags(id="taglist", items=c.libgroup.tags) | n}
<br/>
<br/>

<h2>${_('notes')}</h2>
<a href="${tg.url('/note/%s/new' % c.libgroup.id)}"
   rel="#overlay" class="overlay button">add note</a>
${c.t_notes(id="notestable", items=c.libgroup.notes,
                                    annotable_id=c.libgroup.annotable.id) | n}

