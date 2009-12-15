<%inherit file="spam.templates.tab"/>

<a href="${tg.url('/asset/%s/%s/%s/new' % (c.project.id, container_type, container_id))}"
   rel="#overlay" class="overlay button">new asset</a>

<br/>
<br/>
% for cat, assets in assets_per_category.iteritems():
    <div id="${'toggle_%s' % cat}" class="toggle ${len(assets)==0 and 'hidden' or ''}">
        <div class="toggle_header title">
            <span class="toggle_arrow"/>
            <span class="toggle_title">${cat}</span>
        </div>
        <div class="toggleable">
            ${c.t_assets(id="assets_%s_%s_%s" % (container_type, container_id, cat),
                         items=assets, category=cat,
                         update_listener_adder="notify.add_listener_tab") | n}
        </div>
    </div>
% endfor

## we load the stomp client in case there's no livetable on the page (this can
## happen if the container has no assets). The <script> tag will be put in
## the <head> section inherited from "spam.templates.tab"
${c.j_notify_client()}
<script type="text/javascript">
    spam.temp.reload_tab = function() {
        console.log('spam.temp.reload_tab');
        $(".pane.ajax").load("${tg.url('/asset/%s/%s/%s/' % (c.project.id, container_type, container_id))}");
    }
    spam.temp.current_categories = [];
    % for cat in assets_per_category:
        spam.temp.current_categories.push("${cat}");
    % endfor
    console.log('spam.temp.current_categories', $.inArray("uncategorized", spam.temp.current_categories));
    
    $(function() {
        notify.add_listener("/topic/assets", function(msg) {
            if ($.inArray(msg.ob.category.name, spam.temp.current_categories)<0) {
                spam.temp.reload_tab();
            }
        })
    });
</script>

