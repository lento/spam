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

