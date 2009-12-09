livetable = new(Object);

livetable.field_makers = {}
livetable.sorting = {}

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

livetable.update_sorter = function(table_id, callback) {
    var table = $("#" + table_id);
    table.trigger("update");
    if ($("tbody tr", table).length > 0) {
        table.one("sortEnd", function(e) {
            if (typeof(callback) != 'undefined') {
                callback();
            }
        });
        table.trigger("sorton", [table[0].config.sortList]);
    }
}

livetable.addrow = function(table_id, item, show_update) {
    var show_update = typeof(show_update) != 'undefined' ? show_update : true;

    var table = $("#" + table_id);
    var row = $('<tr id="' + table_id + '_' + item.id + '"></tr>');
    var field_makers = livetable.field_makers[table_id];
    
    if (field_makers != null && typeof(field_makers) != "undefined") {
        $.each(field_makers, function() {
            if (this.condition(item)) {
                var id = this.id;
                var field_class = this.field_class;
                var field_maker = this.maker;
                row.append('<td class="' + field_class + '">' + field_maker(item, id) + '</td>');
            }
        });
    };
    
    $("tbody", table).append(row);
    if (show_update) {
        livetable.update_sorter(table_id, function() {
            row.showUpdates();
        });
    } else {
        livetable.update_sorter(table_id);
    }

    /* activate overlay */
    $(".overlay", row).overlay(function() {
        var trigger = this.getTrigger();
        var target = trigger.attr("href");
        var iframe = $("#overlay iframe")[0];
        iframe.src = target;
    });
}

livetable.deleterow = function(table_id, item, show_update) {
    //var show_update = typeof(show_update) != 'undefined' ? show_update : true;
    // show_update is ignored here, somehow jquery animations don't play nice
    
    var table = $("#" + table_id);
    var row = $("#" + table_id + "_" + item.id, table);
    
    row.remove();
    livetable.update_sorter(table_id);
}

livetable.updaterow = function(table_id, item, show_update) {
    livetable.deleterow(table_id, item, show_update);
    livetable.addrow(table_id, item, show_update);
}

