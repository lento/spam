<%
    from spam.lib.jsonify import encode as json_encode
%>

<script type="text/javascript">
    $(function() {
        livelist.field_makers["${id}"] = [];
        % for index, field in enumerate(fields):
            livelist.field_makers["${id}"].push(
                        {"id": "${field.id}",
                         "field_class": "${field.field_class}",
                         "condition": function(data) {return (${field.condition | n});},
                         "maker": ${field.display().replace('\n', '') | n},
                        });
        % endfor

        $.each(${json_encode(items) | n}, function() {
            livelist.additem("${id}", this, false, ${json_encode(extra_data)});
        });
        
        % if update_topic:
            ${update_listener_adder}("${update_topic}",
                function(msg){
                    if (${update_condition | n}) {
                        $.each(${update_functions}, function(type, func) {
                            if (msg.update_type==type) {
                                func("${id}", msg.ob, true, ${json_encode(extra_data)});
                            }
                        });
                    }
                }
            );
        % endif
    });
</script>


<ul id="${id}">
</ul>
