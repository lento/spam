<%
    from spam.lib.utils import jsonify
%>

<script type="text/javascript">
    addrow = function(table, item, fields, buttons) {
        row = $('<tr></tr>');
        
        if (buttons != null && typeof(buttons) != 'undefined') {
            $.each(buttons, function() {
                row.append('<td class="icon">' +
                           '<div class="iconbutton '+this[0]+'" title="'+this[1]+'">' +
                           '</div></td>');
            });
        };
        
        if (fields == null || typeof(fields) == 'undefined') {
            fields = [];
            $.each(item, function(name, value) {
                fields.push(name);
            });
        };
        
        $.each(fields, function() {
            row.append('<td>'+item[this]+'</td>');
        });
        
        $("tbody", table).append(row);
    }
    
    $(function() {
        $.each(${jsonify(items) | n}, function() {
            addrow($("#${id}"), this, 
                   ${fields and jsonify(fields) or 'null' | n},
                   ${buttons and jsonify(buttons) or 'null' | n});
        });
        
        $("table tr:even").addClass("even");
    });
</script>

<table id="${id}">
    <tbody></tbody>
</table>

