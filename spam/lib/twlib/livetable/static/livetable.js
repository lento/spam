livetable = new(Object);

livetable.field_makers = {}

$.fn.showUpdates = function(callback) {
    return this.each(function() {
        $(this).addClass('updated', "slow", function() {
            $(this).removeClass("updated", "slow", function() {
                if (typeof(callback) != 'undefined')
                    callback();
            });
        });
    });
}

/*
livetable.zebra = function(table_id) {
    console.log('livetable.zebra', table_id);
    var table = $("#" + table_id);
    $("tr:even", table).removeClass("odd").addClass("even");
    $("tr:odd", table).removeClass("even").addClass("odd");
}
*/
livetable.update_sorter = function(table_id) {
    var table = $("#" + table_id);
    table.trigger("update").trigger("sorton", [[[7,0]]]);
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
    
    livetable.update_sorter(table_id);
    
    /* activate overlay */
    $(".overlay", row).overlay(function() {
        trigger = this.getTrigger();
        target = trigger.attr("href");
        iframe = $("#overlay iframe")[0];
        iframe.src = target
    });
}

livetable.deleterow = function(table_id, item, show_update) {
    //var show_update = typeof(show_update) != 'undefined' ? show_update : true;
    // show_update is ignored here, somehow jquery animations don't play nice
    
    var table = $("#" + table_id);
    var row = $("#" + table_id + "_" + item.id, table);
    console.log('livetable.deleterow: ', table_id, item, show_update, row);
    
    row.remove();
    livetable.update_sorter(table_id);
}

livetable.updaterow = function(table_id, item, show_update) {
    livetable.deleterow(table_id, item, show_update);
    livetable.addrow(table_id, item, show_update);
}

