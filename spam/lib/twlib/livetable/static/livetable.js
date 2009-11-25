livetable = new(Object);

livetable.field_makers = {}

$.fn.showUpdates = function() {
    return this.each(function() {
        $(this).addClass('updated', "slow", function () {
            $(this).removeClass("updated", "slow");
        });
    });
}

livetable.addrow = function(table_id, item, show_update) {
    var show_update = typeof(show_update) != 'undefined' ? show_update : true;

    var table = $("#" + table_id);
    var row = $('<tr id="' + table_id + '_' + item.id + '"></tr>');
    var field_makers = livetable.field_makers[table_id];
    
    if (field_makers != null && typeof(field_makers) != "undefined") {
        $.each(field_makers, function() {
            id = this.id;
            field_class = this.field_class;
            field_maker = this.maker;
            row.append('<td class="' + field_class + '">' + field_maker(item, id) + '</td>');
        });
    };
    
    $("tbody", table).append(row);
    if (show_update) {
        row.showUpdates();
    }
}

livetable.deleterow = function(table_id, item, show_update) {
    var show_update = typeof(show_update) != 'undefined' ? show_update : true;

    var table = $("#" + table_id);
    var row = $("#" + table_id + "_" + item.id, table);
    
    if (show_update) {
        row.showUpdates();
    }
    row.fadeOut(function() {
        row.remove();
    });
}

