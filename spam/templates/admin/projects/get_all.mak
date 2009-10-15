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
    <a href="${tg.url('./new')}" rel="#overlay" class="overlay">new project</a>
    <br/>
    <br/>
    <ul>
        % for project in projects:
            <li>${project.name}</li>
        % endfor
    </ul>
</div>

