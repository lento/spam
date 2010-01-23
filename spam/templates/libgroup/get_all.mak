<%inherit file="spam.templates.tab"/>

<%
    new_url = hasattr(c, 'parent') and '%s/%s' % (c.project.id, c.parent.id) or c.project.id
%>

<a href="${tg.url('/libgroup/%s/new' % new_url)}" rel="#overlay" class="overlay button">
    new libgroup
</a>
<br/>
<br/>
${c.t_libgroups(items=libgroups,
    update_listener_adder="notify.add_listener_tab", parent_id=parent_id) | n}

