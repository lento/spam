livetable = new(Object);

livetable.addrow = function(table, item, field_makers) {
    row = $('<tr></tr>');
    
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

