function(data) {
    field = '<a class="iconbutton overlay ${icon_class or ''}" title="${label_text or ''}" ' +
            'href="${action or '' | n}" ' +
            'rel="#overlay" ' +
            '></a>';
    return field;
}
