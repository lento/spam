## the following line is just to have the file sintax-highlighted in gedit ;)
##<script type="text/javascript">

/**********************************************************************
 * STOMP client
 **********************************************************************/
if (typeof(spam.stomp)=='undefined') {
    spam.stomp = new(Object);
    spam.stomp.is_connected = false;

    spam.stomp.host = "${tg.config.get('stomp_host', 'localhost')}";
    spam.stomp.port = ${tg.config.get('stomp_port', '61613')};

    spam.stomp.listeners = [];
    spam.stomp.subscribes = new(Object);
}
/* listeners_tab is reinitialized on every load, so listeners defined in tabs
 * don't pile up when switching tabs*/
spam.stomp.listeners_tab = [];

spam.stomp.add_listener = function(dest, callback) {
    if (spam.stomp.is_connected) {
        spam.stomp.listeners.push({'destination': dest, 'callback': callback});
        console.log('stomp: add_listener ', dest, spam.stomp.listeners, spam.stomp.listeners_tab);
        if (!(dest in spam.stomp.subscribes)) {
            spam.stomp.client.subscribe(dest);
            spam.stomp.subscribes[dest] = 1;
            console.log('stomp: subscribed: ', dest);
        }
    } else {
        setTimeout(function() {spam.stomp.add_listener(dest, callback);}, 250);
    }
}

spam.stomp.add_listener_tab = function(dest, callback) {
    if (spam.stomp.is_connected) {
        spam.stomp.listeners_tab.push({'destination': dest, 'callback': callback});
        console.log('stomp: add_listener_tab ', dest, spam.stomp.listeners, spam.stomp.listeners_tab);
        if (!(dest in spam.stomp.subscribes)) {
            spam.stomp.client.subscribe(dest);
            spam.stomp.subscribes[dest] = 1;
            console.log('stomp: subscribed: ', dest);
        }
    } else {
        setTimeout(function() {spam.stomp.add_listener_tab(dest, callback);}, 250);
    }
}

spam.stomp.start_client = function(){
    document.domain=document.domain;
    
    // if the orbited server has not started STOMPClient won't be available
    if (typeof(STOMPClient)=='undefined') {
        console.log('stomp: STOMPClient not loaded, notifications will not ' +
                    'be available');
        return null;
    }
    
    /* check if the client is already connected (could happen in a ajax tab,
     * for example) */
    if (spam.stomp.is_connected) {
        return;
    }
    
    stomp = new STOMPClient();
    stomp.onopen = function() {
        console.log('stomp: open');
    };
    stomp.onclose = function(c) {
        console.log('stomp: Lost Connection, Code: ', c, ' ...reconnecting');
        spam.stomp.is_connected = false;
        setTimeout(function() {stomp.connect(spam.stomp.host, spam.stomp.port)}, 10000);
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
        $.each(spam.stomp.listeners_tab, function(i,l){
            if (frame.headers.destination==l.destination) {
                l.callback(JSON.parse(frame.body));
            }
        });
    };
    
    stomp.connect(spam.stomp.host, spam.stomp.port);
    console.log('stomp: started stomp client ', spam.stomp.host, spam.stomp.port);
    
    spam.stomp.client =  stomp;
}

/* start the client on page load */
$(function() {
    spam.stomp.start_client();
});

