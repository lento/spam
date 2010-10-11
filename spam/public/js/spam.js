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
                if ($.cookie('spam_toggle_'+id)=="expanded")
                    $(this).addClass("expanded");
                else if ($.cookie('spam_toggle_'+id)=="collapsed")
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
                    $.cookie('spam_toggle_'+id, "collapsed", {path: cookiebase});
            } else {
                $('> .toggleable', toggle).show('fast');
                if (id)
                    $.cookie('spam_toggle_'+id, "expanded", {path: cookiebase});
            }
            toggle.toggleClass('expanded');
            return false;
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
     * Notification
     ****************************************/
    spam.notify = function(msg, status) {
        $("#notify div").attr("class", status).html(msg).slideDown(function() {
            setTimeout(function() {
                $("#notify div").slideUp();
            }, 2500);
        });
    }


    /****************************************
     * tw2.livewidgets
     ****************************************/
    if (typeof(lw)!='undefined') {
        spam.widget_update = lw.update;
    } else {
        spam.widget_update = function() {};
    }


    /****************************************
     * Actions
     ****************************************/
    spam.action = function(target, formdata) {
        formdata = typeof(formdata)!='undefined' ? formdata : null;
        var xhr = new XMLHttpRequest();
        var method = formdata ? "POST" : "GET"
        xhr.open(method, target, false);
        xhr.send(formdata);
        if (xhr.status == 200 || xhr.status == 0) {
            if (xhr.getResponseHeader("Content-Type") == 'application/json; charset=utf-8') {
                var result = JSON.parse(xhr.responseText);
                $.each(result.updates, function() {
                    var topic = this.topic;
                    var item = this.item;
                    var type = this.type!=null ? this.type : 'updated';
                    var show_updates = this.show_updates!=null ? this.show_updates : true;
                    var extra_data = this.extra_data!=null ? this.extra_data : {};
                    var filter = this.filter!=null ? this.filter : '';
                    spam.widget_update(topic, type, item, show_updates, extra_data, filter);
                });
                spam.notify(result.msg, result.status);
                return {'status':'ok', 'xhr': xhr};
            } else {
                return {'status':'notjson', 'xhr': xhr};
            }
        } else {
            spam.notify(xhr.statusText, 'error');
            return {'status':'error', 'xhr': xhr};
        }
    }


    /****************************************
     * Dialog
     ****************************************/
	spam.dialog_load = function(elem) {
        $("#dialog").dialog("destroy").dialog({
	        modal: true,
            width: 500,
	        height: 350,
	        closeText: '',
        });
        $(".ui-dialog").addClass("loading");
        $("#dialog").hide().html("").load(elem.href, function(response, status, xhr) {
            $(".ui-dialog").removeClass("loading");
            if (status=='error') {
	            $(".ui-dialog-titlebar > span").html("error: " + xhr.status);
                $("#dialog").html(xhr.statusText);
            } else {
                $("#dialog h1").hide();
                $(".ui-dialog-titlebar > span").html($("#dialog h1").html());
            }
            $("#dialog").fadeIn();
        });
    }

    spam.submit_dialog = function(form) {
        $(form).addClass("loading");
        $("#submit", form).attr("disabled", "disabled");
        var target = $(form).attr("action") + '.json';
        var formdata = form.getFormData();
        var result = spam.action(target, formdata);
        $(form).removeClass("loading");
        $("#submit", form).removeAttr("disabled");

        if (result.status=='ok') {
            $("#dialog").dialog("destroy");
        } else if (result.status=='notjson') {
            $("#dialog").hide().html(result.xhr.responseText);
            $("#dialog h1").hide();
            $("#dialog").fadeIn();
        } else {
            $("#dialog").dialog("destroy");
        }
    }


    /****************************************
     * Startup function
     ****************************************/
    $(function() {
        spam.toggles_activate();

        /* make #flash slide in and out */
        $("#flash div").hide().slideDown(function() {
            setTimeout(function() {
                $("#flash div").slideUp();
            }, 2500);
        });

	    /* instrument action buttons */
	    $(".action").live("click", function(e) {
	        spam.action($(this).attr("href"));
	        return false;
        });

	    /* instrument dialog buttons */
	    $(".dialog").live("click", function(e) {
	        spam.dialog_load(this);
	        return false;
        });
     });
}


