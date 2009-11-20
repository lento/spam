function(data, id) {
    field = '<a class="iconbutton overlay ${icon_class or ''}" title="${label_text or ''}" ' +
            'href="' + $.sprintf('${action or '' | n}', data) + '" ' +
            'rel="#overlay" ' +
            '></a>';
    return field;
}

