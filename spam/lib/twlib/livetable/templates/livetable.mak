<%
    from spam.lib.utils import jsonify
%>

<script type="text/javascript">
    $(function() {
        rendered_buttons = ${jsonify([b.display() for b in buttons]) | n};
        
        $.each(${jsonify(items) | n}, function() {
            livetable.addrow($("#${id}"), this, 
                             ${fields and jsonify(fields) or 'null' | n},
                             rendered_buttons
            );
        });
        
        $("table tr:even").addClass("even");
        $("table tr:odd").addClass("odd");
    });
</script>

<table id="${id}">
    <tbody></tbody>
</table>

