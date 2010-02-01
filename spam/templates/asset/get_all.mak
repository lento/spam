<%inherit file="spam.templates.tab"/>

% if c.predicates.is_project_admin():
<a href="${tg.url('/asset/%s/%s/%s/new' % (c.project.id, container_type, container_id))}"
   rel="#overlay" class="overlay button">new asset</a>
<br/>
<br/>
% endif

% for cat in container.categories:
    <div id="${'toggle_%s' % cat.id}" class="toggle ${len(container.assets[cat])==0 and 'hidden' or ''}">
        <div class="toggle_header title">
            <span class="toggle_arrow"/>
            <h2 class="toggle_title">${cat.id}</h2>
            ${c.b_status(id="status_%s_%s_%s" % (container_type, container_id, cat.id),
                         items=container.assets[cat], container_id=container_id,
                         category_id=cat.id,
                         update_listener_adder="notify.add_listener_tab") | n}
        </div>
        <div class="toggleable">
            ${c.t_assets(id="assets_%s_%s_%s" % (container_type, container_id, cat.id),
                         items=container.assets[cat], category=cat.id,
                         update_listener_adder="notify.add_listener_tab",
                         extra_data=dict(user_id=c.user.id)) | n}
        </div>
    </div>
% endfor

## we load the stomp client in case there's no livetable on the page (this can
## happen if the container has no assets). The <script> tag will be put in
## the <head> section inherited from "spam.templates.tab"
${c.j_notify_client()}
<script type="text/javascript">
    spam.temp.reload_tab = function() {
        $(".pane.ajax").load("${tg.url('/asset/%s/%s/%s/' % (c.project.id, container_type, container_id))}");
    }
    spam.temp.current_categories = [];
    % for cat in container.categories:
        spam.temp.current_categories.push("${cat.id}");
    % endfor
    
    $(function() {
        notify.add_listener_tab("/topic/assets", function(msg) {
            if ($.inArray(msg.ob.category.id, spam.temp.current_categories)<0) {
                spam.temp.current_categories.push(msg.ob.category.id);
                spam.temp.reload_tab();
            }
        })
    });
</script>

