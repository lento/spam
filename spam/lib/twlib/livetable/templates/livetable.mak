<%
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
            livetable.field_makers["${id}"].push({"id": "${field.id}", "field_class": "${field.field_class}", "maker": ${field.display().replace('\n', '') | n}});
        % endfor
        
        $("#${id}").tablesorter({widgets: ['zebra'], headers: ${json_encode(sort_headers)}});

        $.each(${json_encode(items) | n}, function() {
            livetable.addrow("${id}", this, false);
        });
        
        % if sort_list and items:
            $("#${id}").trigger("sorton", [${json_encode(sort_list)}]);
        % endif
        
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
    <thead class="${not show_headers and 'hidden' or ''}">
        <tr>
            % for field in fields:
                <th>${field.show_header and field.id or ''}</th>
            % endfor
        </tr>
    </thead>
    <tbody></tbody>
</table>

