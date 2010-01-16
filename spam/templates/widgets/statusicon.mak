function(data, id) {
    field = '<div class="statusicon ${icon_class or ''} ' + data[id] + '" ' +
    % if label_text:
        'title="${label_text}' + data[id] + '"' +
    % else:
        'title="' + data.name + ': ' + data[id] + '"' +
    % endif
    '></div>';
    return field;
}

