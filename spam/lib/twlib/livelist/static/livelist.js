livelist = new(Object);

livelist.field_makers = {}

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

livelist.additem = function(list_id, item, show_update, extra_data) {
    console.log('additem', list_id, item, show_update, extra_data, livelist.field_makers[list_id]);
    var show_update = typeof(show_update) != 'undefined' ? show_update : true;
    var extra_data = typeof(extra_data) != 'undefined' ? extra_data : {};

    var list = $("#" + list_id);
    var li = $('<li id="' + list_id + '_' + item.id + '"></li>');
    var field_makers = livelist.field_makers[list_id];
    
    if (field_makers != null && typeof(field_makers) != "undefined") {
        $.each(field_makers, function() {
            if (this.condition(item)) {
                var id = this.id;
                var field_class = this.field_class;
                var field_maker = this.maker;
                var data = item;
                $.each(extra_data, function(key, value) {data[key] = value;});
                li.append('<span class="' + field_class + '">' + field_maker(data, id) + '</span>');
            }
        });
    };
    
    list.append(li);
    if (show_update) {
        item.showUpdates();
    }

    /* activate overlay */
    $(".overlay", item).overlay(function() {
        var trigger = this.getTrigger();
        var target = trigger.attr("href");
        var iframe = $("#overlay iframe")[0];
        iframe.src = target;
    });
}

livelist.deleteitem = function(list_id, item, show_update) {
    //var show_update = typeof(show_update) != 'undefined' ? show_update : true;
    // show_update is ignored here, somehow jquery animations don't play nice
    
    var list = $("#" + list_id);
    var item = $("#" + list_id + "_" + item.id, list);
    
    item.remove();
}

livelist.updateitem = function(list_id, item, show_update) {
    livelist.deleteitem(list_id, item, show_update);
    livelist.additem(list_id, item, show_update);
}

