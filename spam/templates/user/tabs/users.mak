<%inherit file="spam.templates.tab"/>

<a href="${tg.url('./new')}" rel="#overlay" class="overlay button">new user</a>
<br/>
<br/>
<h1>${_('Users')}</h1>
${c.t_users(id='users', items=list(users),
            update_listener_adder="notify.add_listener_tab") | n}

