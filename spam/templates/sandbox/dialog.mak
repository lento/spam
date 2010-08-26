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
	    $("#dialog").dialog({
		    //height: 140,
		    modal: true,
		    draggable: true,
		    resizable: true,
		    autoOpen: false,
		    closeText: '',
	    });
    });
</script>

<div class="content">
    <a onClick="$('#dialog').dialog('open')">open</a>
    <br/>
    <br/>

    <div id="dialog" title="un titolo">
	    <p>Adding the modal overlay screen makes the dialog look more prominent because it dims out the page content.</p>
    </div>
</div>


