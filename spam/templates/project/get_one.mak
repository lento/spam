<%inherit file="spam.templates.master"/>

<script type="text/javascript">
    /* we make sure the url pathname has a trailing slash so we can use relative
     * paths for panes */
    spam.add_trailing_slash();
</script>

<!-- the tabs --> 
<ul class="tabs"> 
    <li><a id="summary" href="tab/summary">Summary</a></li> 
    <li><a id="scenes" href="tab/scenes">Scenes</a></li> 
    <li><a id="tasks" href="tab/tasks">Tasks</a></li> 
</ul> 
 
<!-- tab "panes" --> 
<div class="panes"> 
    <div class="pane" style="display:block"></div> 
</div>


