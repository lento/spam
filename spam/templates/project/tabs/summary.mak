<%inherit file="spam.templates.tab"/>

<h2>${_('scenes')}</h2>
${c.b_status(id="status_%s_scenes" % (c.project.id), items=c.project.scenes) | n}
<br/>
<br/>

<h2>${_('library')}</h2>
${c.b_status(id="status_%s_library" % (c.project.id), items=c.project.libgroups) | n}
<br/>
<br/>

