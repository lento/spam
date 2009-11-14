<%
    from spam.lib.utils import jsonify
%>

<script type="text/javascript">
    $(function() {
        field_makers = [];
        % for field in fields:
            field_makers.push({'id': '${field.id}', 'field_class': '${field.field_class}', 'maker': ${field.display() | n}});
        % endfor
        
        $.each(${jsonify(items) | n}, function() {
            livetable.addrow($("#${id}"), this, field_makers);
        });
        
        $("table tr:even").addClass("even");
        $("table tr:odd").addClass("odd");
    });
</script>

<table id="${id}">
    <tbody></tbody>
</table>

