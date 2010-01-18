function(data, id) {
    var field = '<div class="statusiconbox">';
    console.log('statusiconbox', data, id);
    $.each(data[id], function(index, item) {
        field += '<div class="statusicon ' + item['name'] + ' ' + item['status'] + '" ' +
            'title="' + item['name'] + ': ' + item['status'] + '"' +
        '></div>';
    });
    field += '</div>';
    return field;
}

