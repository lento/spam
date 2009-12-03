<%inherit file="spam.templates.standalone"/>

<%def name="style()">
    <link rel="stylesheet" type="text/css" media="screen" href="${tg.url('/themes/%s/css/form.css' % c.theme)}" />
</%def>

<script type="text/javascript">
    $(function() {
        $("label", $("input:disabled").parent()).addClass('disabled');
    });
</script>

<h1>${title}</h1>
    % if msg:
        <div class="msg">${msg}</div>
    % endif
    % if warning:
        <div class="warning">${warning}</div>
    % endif
    ${c.form(args, child_args=child_args) | n}

