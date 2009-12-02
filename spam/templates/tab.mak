## the head section is needed to inject javascripts that come with widgets
<head></head>

<script type="text/javascript">
    spam.toggles_activate(".pane.ajax");
    spam.overlays_activate(".pane.ajax");
    if (typeof(spam.stomp)!='undefined') {
        spam.stomp.add_listener = spam.stomp.add_listener_tab;
    }
</script>

<div>
    ${self.body()}
</div>

