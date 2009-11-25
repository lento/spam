<%
    from spam.lib.jsonify import encode as json_encode
%>

<script type="text/javascript">
    $(function() {
        livetable.field_makers["${id}"] = [];
        % for field in fields:
            livetable.field_makers["${id}"].push({"id": "${field.id}", "field_class": "${field.field_class}", "maker": ${field.display().replace('\n', '') | n}});
        % endfor
        
        $.each(${json_encode(items) | n}, function() {
            livetable.addrow("${id}", this, false);
        });
        
        $("#${id} tr:even").addClass("even");
        $("#${id} tr:odd").addClass("odd");

        /* activate overlay */
        $(".overlay", $("#${id}")).overlay(function() { 
            trigger = this.getTrigger();
            target = trigger.attr("href");
            iframe = $("#overlay iframe")[0];
            iframe.src = target
        });
        
        % if update_topic:
            spam.stomp.add_listener("${update_topic}",
                function(data){
                    if (${update_condition | n}) {
                        $.each(${update_functions}, function(type, func) {
                            if (data.update_type==type) {
                                func("${id}", data.ob);
                            }
                        });
                    }
                }
            );
        % endif
    });
</script>

<table id="${id}">
    <tbody></tbody>
</table>

