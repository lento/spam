## This file is part of SPAM (Spark Project & Asset Manager).
##
## SPAM is free software: you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
##
## SPAM is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with SPAM.  If not, see <http://www.gnu.org/licenses/>.
##
## Original Copyright (c) 2010, Lorenzo Pierfederici <lpierfederici@gmail.com>
## Contributor(s): 
##

function(data, id) {
    var field = '<div class="statusiconbox">';
    $.each(data[id], function(index, item) {
        field += '<div class="statusicon ' + item['name'] + ' ' + item['status'] + '" ' +
            'title="' + item['name'] + ': ' + item['status'] + '"' +
        '></div>';
    });
    field += '</div>';
    return field;
}

