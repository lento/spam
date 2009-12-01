function(data, id) {
    src = (data[id]) ? data[id] : '';
    field = '<img src="' + src + '"></img>';
    return field;
}

