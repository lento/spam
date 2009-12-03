<%inherit file="spam.templates.tab"/>

<a href="${tg.url('/asset/%s/%s/%s/new' % (c.project.id, container_type, container_id))}"
   rel="#overlay" class="overlay button">new asset</a>
<br/>
<br/>
% for cat, assets in categories.iteritems():
    <div id="temp_toggle" class="toggle">
        <div class="toggle_header title">
            <span class="toggle_arrow"/>
            <span class="toggle_title">${cat}</span>
        </div>
        <div class="toggleable">
            ${c.t_assets(items=assets) | n}
        </div>
    </div>
% endfor

