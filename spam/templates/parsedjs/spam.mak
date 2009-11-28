## the following line is just to have the file sintax-highlighted in gedit ;)
##<script type="text/javascript">

/* we put all our functions and objects inside "spam" so we don't clutter
 * the namespace */
spam = new(Object);

/* if firebug is not active we create a fake "console" */
if (typeof(console)=="undefined") {
    console = new(Object);
    console.log = function() {};
}

/* for some pages we need to make sure that the url pathname has a trailing
 * slash, so we can use relative paths (tabs, for an example) */
spam.add_trailing_slash = function() {
    if (!window.location.pathname.match(/\/$/))
        window.location.replace(window.location.pathname + '/' +
                                window.location.search + window.location.hash);
}

/**********************************************************************
 * Toggles
 **********************************************************************/
spam.toggles_activate = function (select) {
    if (typeof(select)=="undefined" || select==null) {
        select = "";
    }
    console.log('toggles_activate', select);
    
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
    $(select + ".toggle_arrow").click(function(event){
        toggle = $(this).parents(".toggle:first");
        id = toggle.attr("id");
        
        if (toggle.hasClass('expanded')) {
            $('> .toggleable', toggle).hide('fast');
            if (id)
                $.cookie(id, "collapsed", {path: "${tg.url('/')}"});
        } else {
            $('> .toggleable', toggle).show('fast');
            if (id)
                $.cookie(id, "expanded", {path: "${tg.url('/')}"});
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
    console.log('overlays_activate', select);
    $(select + " .overlay").overlay(function() { 
        trigger = this.getTrigger();
        target = trigger.attr("href");
        iframe = $("#overlay iframe")[0];
        iframe.src = target
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
        }, 4000);
    });

    // setup ul.tabs to work as tabs for each div.pane directly under div.panes 
    $(".tabs").tabs(".content > .pane", {effect: 'ajax'}).history();
});

##</script>

