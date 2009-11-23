function(data, id) {
    if (data["schema_is_uptodate"]) {
        icon_class = "schema_uptodate";
        action = "${action['uptodate'] | n}";
        label_text = "DB schema is up to date";
    } else {
        icon_class = "schema_outdated";
        action = "${action['outdated'] | n}";
        label_text = "DB schema is outdated, click to upgrade";
    }
    action_str = (action) ? 'href="' + $.sprintf(action, data) + '" rel="#overlay" ' : '';
    field = '<a class="iconbutton overlay ' + icon_class +'" title="' + label_text + '" ' +
            action_str +
            '></a>';
    return field;
}

