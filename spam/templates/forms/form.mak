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

<script type="text/javascript">
    spam.submit_dialog = function(form) {
        $(form).addClass("loading");
        $("#submit", form).attr("disabled", "disabled");
        var action = $(form).attr("action") + '.json';
        var xhr = new XMLHttpRequest();
        xhr.open("POST", action, false);
        xhr.send(form.getFormData());
        $(form).removeClass("loading");
        $("#submit", form).removeAttr("disabled");
        if (xhr.status == 200) {
            if (xhr.getResponseHeader("Content-Type") == 'application/json; charset=utf-8') {
                var result = JSON.parse(xhr.responseText);
                $.each(result.updates, function() {
                    var topic = this.topic;
                    var item = this.item;
                    var type = this.type!=null ? this.type : 'updated';
                    var show_updates = this.show_updates!=null ? this.show_updates : true;
                    var extra_data = this.extra_data!=null ? this.extra_data : {};
                    var filter = this.filter!=null ? this.filter : '';
                    spam.widget_update(topic, type, item, show_updates, extra_data, filter);
                });
                spam.notify(result.msg, result.status);
                $("#dialog").dialog("destroy");
            } else if (xhr.getResponseHeader("Content-Type") == 'text/html; charset=utf-8') {
                console.log(xhr.getResponseHeader("Content-Type"));
                $("#dialog").hide().html(xhr.responseText);
                $("#dialog h1").hide();
                $("#dialog").fadeIn();
            } else {
                spam.notify('error', 'error');
            }
        } else {
            spam.notify(xhr.statusText, 'error');
        }
    }

    $(function() {
        $("#dialog form").bind("submit", function() {
            spam.submit_dialog(this);
            return false;
        });
    });
</script>

<div class="form">
    <h1>${title}</h1>
        % if msg:
            <div class="msg">${msg}</div>
        % endif
        % if warning:
            <div class="warning">${warning}</div>
        % endif
        ${c.form.display() | n}
</div>
