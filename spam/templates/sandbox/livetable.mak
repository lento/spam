<%inherit file="spam.templates.standalone"/>

<h2>LiveTable test</h2>
<br/>
<br/>
${c.t_test(id='test', items=items) | n}
