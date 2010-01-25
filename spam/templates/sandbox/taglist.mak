<%inherit file="spam.templates.standalone"/>

<h2>tags for ${shot.path}</h2>
<br/>
${c.b_tags(id="taglist", items=tags) | n}
