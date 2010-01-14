<%
    import cgi
    from spam.lib.jsonify import encode as json_encode
    sort_list = []
    sort_headers = {}
    for index, field in enumerate(fields):
        if not field.sortable:
            sort_headers[index] = dict(sorter=False)
        if field.sort_default:
            direction = field.sort_direction=='desc' and 1 or 0
            sort_list.append([index, direction])
%>

<script type="text/javascript">
    $(function() {
        livetable.field_makers["${id}"] = [];
        % for index, field in enumerate(fields):
            livetable.field_makers["${id}"].push(
                        {"id": "${field.id}",
                         "field_class": "${field.field_class}",
                         "condition": function(data) {return (${field.condition | n});},
                         "maker": ${field.display().replace('\n', '') | n},
                        });
        % endfor
        
        $("#${id}").tablesorter({widgets: ['zebra'], headers: ${json_encode(sort_headers)}});

        $.each(${cgi.escape(json_encode(items)) | n}, function() {
            livetable.addrow("${id}", this, false, ${json_encode(extra_data)});
        });
        
        % if sort_list and items:
            $("#${id}").trigger("sorton", [${json_encode(sort_list)}]);
        % endif
        
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

<table id="${id}">
    <thead class="${not show_headers and 'hidden' or ''}">
        <tr>
            % for field in fields:
                <th>${field.show_header and field.id or ''}</th>
            % endfor
        </tr>
    </thead>
    <tbody></tbody>
</table>

