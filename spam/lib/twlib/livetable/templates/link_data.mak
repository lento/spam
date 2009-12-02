function(data, id) {
    text = (data[id]) ? data[id] : '';
    dest = $.sprintf('${dest or '' | n}', data);
    field = '<div><a href="' + dest + '">' + text + '</a></div>';
    return field;
}
