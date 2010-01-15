function(data, id) {
    field = '<div class="statusicon ${icon_class or ''} ' + data[id] + '" ' +
    'title="${label_text and '%s: ' % label_text or ''}' + data[id] + '"></div>';
    return field;
}

