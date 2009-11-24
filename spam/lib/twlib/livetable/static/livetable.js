livetable = new(Object);

livetable.field_makers = {}

livetable.addrow = function(table_id, item) {
    table = $("#" + table_id);
    row = $('<tr></tr>');
    field_makers = livetable.field_makers[table_id];
    
    if (field_makers != null && typeof(field_makers) != 'undefined') {
        $.each(field_makers, function() {
            id = this.id;
            field_class = this.field_class;
            field_maker = this.maker;
            row.append('<td class="' + field_class + '">' + field_maker(item, id) + '</td>');
        });
    };
    
    $("tbody", table).append(row);
}

