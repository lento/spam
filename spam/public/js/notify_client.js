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

/**********************************************************************
 * STOMP client
 **********************************************************************/
notify_init = function(host, port) {
    if (typeof(notify)=='undefined') {
        console.log('notify is undefined, reloading');
        notify = new(Object);
        notify.is_connected = false;

        notify.host = host;
        notify.port = port;

        notify.listeners = [];
        notify.subscribes = new(Object);
    }
    /* listeners_tab is reinitialized on every load, so listeners defined in tabs
     * don't pile up when switching tabs*/
    notify.listeners_tab = [];

    notify.add_listener = function(dest, callback) {
        if (notify.is_connected) {
            notify.listeners.push({'destination': dest, 'callback': callback});
            console.log('stomp: add_listener ', dest, notify.listeners, notify.listeners_tab);
            if (!(dest in notify.subscribes)) {
                notify.client.subscribe(dest);
                notify.subscribes[dest] = 1;
                console.log('stomp: subscribed: ', dest);
            }
        } else {
            setTimeout(function() {notify.add_listener(dest, callback);}, 250);
        }
    }

    notify.add_listener_tab = function(dest, callback) {
        if (notify.is_connected) {
            notify.listeners_tab.push({'destination': dest, 'callback': callback});
            console.log('stomp: add_listener_tab ', dest, notify.listeners, notify.listeners_tab);
            if (!(dest in notify.subscribes)) {
                notify.client.subscribe(dest);
                notify.subscribes[dest] = 1;
                console.log('stomp: subscribed: ', dest);
            }
        } else {
            setTimeout(function() {notify.add_listener_tab(dest, callback);}, 250);
        }
    }

    notify.start_client = function(){
        document.domain=document.domain;
        
        // if the orbited server has not started STOMPClient won't be available
        if (typeof(STOMPClient)=='undefined') {
            console.log('stomp: STOMPClient not loaded, notifications will not ' +
                        'be available');
            return null;
        }
        
        /* check if the client is already connected (could happen in a ajax tab,
         * for example) */
        if (notify.is_connected) {
            return;
        }
        
        stomp = new STOMPClient();
        stomp.onopen = function() {
            console.log('stomp: open');
        };
        stomp.onclose = function(c) {
            console.log('stomp: Lost Connection, Code: ', c, ' ...reconnecting');
            notify.is_connected = false;
            setTimeout(function() {stomp.connect(notify.host, notify.port)}, 10000);
        };
        stomp.onerror = function(error) {
            console.log("stomp: Error: ", error);
        };
        stomp.onerrorframe = function(frame) {
            console.log("stomp: Error: ", frame.body);
        };
        stomp.onconnectedframe = function() {
            console.log('stomp: connected');
            notify.is_connected = true;
        };
        stomp.onmessageframe = function(frame) {
            //console.log('stomp: message frame', frame);
            $.each(notify.listeners, function(i,l){
                if (frame.headers.destination==l.destination) {
                    l.callback(JSON.parse(frame.body));
                }
            });
            $.each(notify.listeners_tab, function(i,l){
                if (frame.headers.destination==l.destination) {
                    l.callback(JSON.parse(frame.body));
                }
            });
        };
        
        stomp.connect(notify.host, notify.port);
        console.log('stomp: started stomp client ', notify.host, notify.port);
        
        notify.client =  stomp;
    }

    /* start the client on page load */
    $(function() {
        notify.start_client();
    });
}
