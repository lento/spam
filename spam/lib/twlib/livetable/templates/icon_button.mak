function(data, id) {
    field = '<a class="iconbutton overlay ${icon_class or ''}" title="${label_text or ''}" ' +
            % if action:
                'href="' + $.sprintf('${action or '' | n}', data) + '" ' +
                'rel="#overlay" ' +
            % endif
            '></a>';
    return field;
}

