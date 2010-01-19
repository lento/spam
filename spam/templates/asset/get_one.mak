<%inherit file="spam.templates.standalone"/>

<h4>${asset.path}</h4>
${c.t_history(items=history) | n}

