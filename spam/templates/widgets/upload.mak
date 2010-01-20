<script type="text/javascript">
    $(function() {
        $("#uploader").uploader({target: "${target}",
                                 queue: "${queue}",
                                 submitter: "${submitter}"});
    });
</script>

<input id="uploader" name="${id}" type="file" multiple="true" id="input" />
<br/>
<div id="upload_queue"></div>

