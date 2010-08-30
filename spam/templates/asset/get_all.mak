## SPAM Spark Project & Asset Manager
##
## This file is part of SPAM (Spark Project & Asset Manager).
##
## SPAM is free software: you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
##
## SPAM is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with SPAM.  If not, see <http://www.gnu.org/licenses/>.
##
## Original Copyright (c) 2010, Lorenzo Pierfederici <lpierfederici@gmail.com>
## Contributor(s): 
##

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
##            ${c.b_status(id="status_%s_%s_%s" % (container_type, container_id, cat.id),
##                         items=container.assets[cat], container_id=container_id,
##                         category_id=cat.id,
##                         update_listener_adder="notify.add_listener_tab") | n}
        </div>
        <div class="toggleable">
            ${c.t_assets(id="assets_%s_%s_%s" % (container_type, container_id, cat.id),
                    value=container.assets[cat],
                    category=cat.id,
                    update_listener_adder="notify.add_listener_tab",
                    extra_data=dict(user_id=c.user.id),
                ).display() | n}
        </div>
    </div>
% endfor

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

