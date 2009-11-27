<%inherit file="spam.templates.master"/>

<script type="text/javascript">
    $(function() {
        if (!window.location.pathname.match(/\/$/)) {
            window.location.replace(window.location.pathname + '/' +
                                    window.location.search + window.location.hash);
        }
    });
</script>


<h2>location</h2>
${args}
<br/>
${kwargs}
