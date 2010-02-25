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

<%inherit file="spam.templates.master"/>

<script type="text/javascript">
    $(function() {
        console.log('adding listener');
        spam.stomp.add_listener('/topic/test',
            function(data){
                console.log('received!');
                $("#stomp_messages").append('<div>' + data.text + '</div>');
        });
        
        console.log('listeners: ', spam.stomp.listeners);
        console.log('subscribes: ', spam.stomp.subscribes);
        console.log('stomp.client: ', spam.stomp.client);
    });
</script>


<h2>messages</h2>
<div id="stomp_messages"></div>

