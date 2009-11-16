function(data, id) {
    field = '<a class="iconbutton overlay ${icon_class or ''}" title="${label_text or ''}" ' +
            'href="' + data['id'] + '/${action or '' | n}" ' +
            'rel="#overlay" ' +
            '></a>';
    return field;
}
