livetable = new(Object);

livetable.addrow = function(table, item, fields, buttons) {
    row = $('<tr></tr>');
    
    if (buttons != null && typeof(buttons) != 'undefined') {
        $.each(buttons, function() {
            row.append('<td class="icon">' + this + '</td>');
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


