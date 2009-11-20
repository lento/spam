<%
    from spam.lib.jsonify import encode as json_encode
%>

<script type="text/javascript">
    $(function() {
        field_makers = [];
        % for field in fields:
            field_makers.push({'id': '${field.id}', 'field_class': '${field.field_class}', 'maker': ${field.display().replace('\n', '') | n}});
        % endfor
        
        $.each(${json_encode(items) | n}, function() {
            livetable.addrow($("#${id}"), this, field_makers);
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
    });
</script>

<table id="${id}">
    <tbody></tbody>
</table>

