function(data, id) {
    text = (data[id]) ? data[id] : '';
    field = '<div>' + text + '</div>';
    return field;
}
