## the following line is just to have the file sintax-highlighted in gedit ;)
##<script type="text/javascript">
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


/**********************************************************************
 * STOMP client
 **********************************************************************/
spam.stomp = new(Object);

spam.stomp.host = "${tg.config.get('stomp_host', 'localhost')}";
spam.stomp.port = ${tg.config.get('stomp_port', '61613')};

spam.stomp.listeners = [];
spam.stomp.subscribes = new(Object);

spam.stomp.add_listener = function(dest, callback) {
    if (spam.stomp.is_connected) {
        console.log('stomp: add_listener ', dest);
        spam.stomp.listeners.push({'destination': dest, 'callback': callback});
        if (!(dest in spam.stomp.subscribes)) {
            spam.stomp.client.subscribe(dest);
            spam.stomp.subscribes[dest] = 1;
            console.log('stomp: subscribed: ', dest);
        }
    } else {
        setTimeout(function() {spam.stomp.add_listener(dest, callback);}, 250);
    }
}

spam.stomp.start_client = function(){
    console.log('stomp: starting client')
    document.domain=document.domain;
    spam.stomp.is_connected = false;
    
    stomp = new STOMPClient();
    stomp.onopen = function() {
        console.log('stomp: open');
    };
    stomp.onclose = function(c) {
        console.log('stomp: Lost Connection, Code: ', c, ' ...reconnecting');
        spam.stomp.is_connected = false;
        stomp.connect(spam.stomp.host, spam.stomp.port);
    };
    stomp.onerror = function(error) {
        console.log("stomp: Error: ", error);
    };
    stomp.onerrorframe = function(frame) {
        console.log("stomp: Error: ", frame.body);
    };
    stomp.onconnectedframe = function() {
        console.log('stomp: connected');
        spam.stomp.is_connected = true;
    };
    stomp.onmessageframe = function(frame) {
        //console.log('stomp: message frame', frame);
        $.each(spam.stomp.listeners, function(i,l){
            if (frame.headers.destination==l.destination) {
                l.callback(JSON.parse(frame.body));
            }
        });
    };
    
    stomp.connect(spam.stomp.host, spam.stomp.port);
    console.log('stomp: started stomp client ', spam.stomp.host, spam.stomp.port);
    
    return stomp;
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

    spam.stomp.client = spam.stomp.start_client();
});
##</script>
