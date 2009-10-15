spam = new(Object);

/**********************************************************************
 * Toggles
 **********************************************************************/
spam.activate_toggles = function () {
    /* set toggle state based on cookies (toggles without an id are skipped)*/
    $('.toggle').each(function() {
        id = this.id;
        if (id) {
            if ($.cookie(id)=="expanded")
                $(this).addClass("expanded");
            else if ($.cookie(id)=="collapsed")
                $(this).removeClass("expanded");
        }
    });            
    
    /* instrument arrows to open and close the toggle */
    $('.toggle_arrow').click(function(event){
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


/****************************************
 * Sidebar
 ****************************************/
spam.setActiveSidebar = function(sidebar, item) {
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
    spam.activate_toggles();
    
    /* make #flash slide in and out */
    $("#flash div").hide().slideDown(function() {
        setTimeout(function() {
            $("#flash div").slideUp();
        }, 4000);
    });

});

