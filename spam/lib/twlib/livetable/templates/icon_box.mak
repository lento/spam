function(data, id) {
    field = '';
    % for index, button in enumerate(buttons):
        if (${button.condition | n}) {
            button_${index} = ${button.display() | n};
            field += button_${index}(data, "${button.id}");
        }
    % endfor
    return field;
}

