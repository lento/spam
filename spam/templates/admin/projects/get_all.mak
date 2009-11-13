<%inherit file="spam.templates.master"/>

<script type="text/javascript">
    $(function() {
        $(".overlay").overlay(function() { 
            trigger = this.getTrigger();
            target = trigger.attr("href");
            iframe = $("#overlay iframe")[0];
            iframe.src = target
        });
    });
</script>

<div>
    <a href="${tg.url('./new')}" rel="#overlay" class="overlay button">new project</a>
    <br/>
    <br/>
    <h1>${_('Active projects')}</h1>
    ${c.active_projects(id='active_projects', items=active) | n}
    <br/>
    <br/>
    <h1>${_('Archived projects')}</h1>
    ${c.archived_projects(id='archived_projects', items=archived) | n}
</div>

