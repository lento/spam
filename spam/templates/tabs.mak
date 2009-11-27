<%inherit file="spam.templates.master"/>

<script type="text/javascript">
    /* we make sure the url pathname has a trailing slash so we can use relative
     * paths for panes */
    spam.add_trailing_slash();
</script>

<!-- the tabs --> 
<ul class="tabs">
    % for name, dest in tabs:
        <li><a href="${dest}">${name}</a></li>
    % endfor
</ul> 
 
<!-- tab "panes" --> 
<div class="panes"> 
    <div class="pane ajax"></div> 
</div>


