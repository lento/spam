function(data, id) {
    src = $.sprintf('${src or '' | n}', data);
    dest = $.sprintf('${dest or '' | n}', data);
    field = '<a href="' + dest + '"><img src="' + src + '"></img></a>';
    return field;
}

