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
        // activate tabs
        $(".tabs").tabs(".content > .pane", {
		    effect: 'fade',
		    onBeforeClick: function(event, i) {
			    var pane = this.getPanes().eq(i);
			    var tab = this.getTabs().eq(i);
			    tab.addClass('loading');
			    pane.load(tab.attr("href"), function() {
			        tab.removeClass('loading');
		        });
		    }
	    }).history();
    });
</script>

<div id="tabbed_content_wrapper"> 
    <!-- the tabs --> 
    <ul class="tabs">
        % for name, dest in tabs:
            <li>
                <a href="${dest}">
                    <div class="icon icon_loading_black"></div>
                    ${name}
                </a>
            </li>
        % endfor
    </ul> 
     
    <!-- tab "panes" --> 
    <div class="content">
        % for name, dest in tabs:
            <div class="pane"></div>
        % endfor
    </div>
</div>

