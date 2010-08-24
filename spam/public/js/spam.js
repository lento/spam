/* This file is part of SPAM (Spark Project & Asset Manager).
 *
 * SPAM is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * SPAM is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with SPAM.  If not, see <http://www.gnu.org/licenses/>.
 *
 * Original Copyright (c) 2010, Lorenzo Pierfederici <lpierfederici@gmail.com>
 * Contributor(s): 
 */

spam_init = function (cookiebase) {
    /* we put all of our functions and objects inside "spam" so we don't clutter
     * the namespace */
    spam = new(Object);
    spam.temp = new(Object);

    /* if firebug is not active we create a fake "console" */
    if (typeof(console)=="undefined") {
        console = new(Object);
        console.log = function() {};
    }

    /**********************************************************************
     * Toggles
     **********************************************************************/
    spam.toggles_activate = function (select) {
        if (typeof(select)=="undefined" || select==null) {
            select = "";
        }

        /* set toggle state based on cookies (toggles without an id are skipped)*/
        $(select + " .toggle").each(function() {
            id = this.id;
            if (id) {
                if ($.cookie(id)=="expanded")
                    $(this).addClass("expanded");
                else if ($.cookie(id)=="collapsed")
                    $(this).removeClass("expanded");
            }
        });            
        
        /* instrument arrows to open and close the toggle */
        $(select + " .toggle_arrow").click(function(event){
            toggle = $(this).parents(".toggle:first");
            id = toggle.attr("id");
            
            if (toggle.hasClass('expanded')) {
                $('> .toggleable', toggle).hide('fast');
                if (id)
                    $.cookie(id, "collapsed", {path: cookiebase});
            } else {
                $('> .toggleable', toggle).show('fast');
                if (id)
                    $.cookie(id, "expanded", {path: cookiebase});
            }
            toggle.toggleClass('expanded');
            return false;
        });

    }


    /**********************************************************************
     * Overlays
     **********************************************************************/
    spam.overlays_activate = function(select) {
        if (typeof(select)=="undefined" || select==null) {
            select = "";
        }

        $(select + " .overlay").overlay({
            onBeforeLoad: function(event) { 
                trigger = this.getTrigger();
                target = trigger.attr("href");
                iframe = $("#overlay iframe")[0];
                iframe.src = target;
            },
            onClose: function(event) { 
                iframe = $("#overlay iframe")[0];
                iframe.src = "about:blank";
            },
            expose: {
                color: '#333'
            }
        });
    }

    /****************************************
     * Sidebar
     ****************************************/
    spam.sidebar_set_active = function(sidebar, item) {
        if (sidebar && item) {
            sbid = "#sb_"+sidebar;
            itemclass = "."+item;
            
            $(sbid).addClass("active");
            $(itemclass, $(sbid)).addClass("active");
        }
    }


    /****************************************
     * Startup function
     ****************************************/
    $(function() {
        spam.toggles_activate();
        spam.overlays_activate();
        
        /* make #flash slide in and out */
        $("#flash div").hide().slideDown(function() {
            setTimeout(function() {
                $("#flash div").slideUp();
            }, 2500);
        });
    });
}


