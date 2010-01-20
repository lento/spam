function(data, id) {
    var field = '<div class="statusicon ${icon_class or ''} ' + data[id] + '" ';
    field += 'title="' + $.sprintf('${label_text or '' | n}', data) + '"';
    field += '></div>';
    return field;
}

