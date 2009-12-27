function(data, id) {
    text = (data[id]) ? data[id] : '';
    dest = $.sprintf('${dest or '' | n}', data);
    field = '<a href="' + dest + '">' + text + '</a>';
    return field;
}

