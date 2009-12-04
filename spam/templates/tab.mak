## the head section is needed to inject javascripts that come with widgets
<head></head>

<script type="text/javascript">
    spam.toggles_activate("#tab_content");
    spam.overlays_activate("#tab_content");
    if (typeof(notify)!='undefined') {
        notify.listeners_tab = [];
    }
</script>

<div id="tab_content">
    ${self.body()}
</div>

