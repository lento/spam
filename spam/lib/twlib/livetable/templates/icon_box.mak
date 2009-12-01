function(data, id) {
    field = '';
    % for index, button in enumerate(buttons):
        button_${index} = ${button.display() | n};
        field += button_${index}(data, "${button.id}");
    % endfor
    return field;
}

