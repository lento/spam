<%inherit file="spam.templates.tab"/>

<h2>${_('scenes')}</h2>
${c.b_scenes_status(id="status_%s_scenes" % c.project.id,
                    items=c.project.scenes, proj_id=c.project.id,
                    update_listener_adder="notify.add_listener_tab") | n}
<br/>
<br/>

<h2>${_('library')}</h2>
${c.b_libgroups_status(id="status_%s_library" % c.project.id,
                    items=c.project.libgroups, libgroup_id=None,
                    update_listener_adder="notify.add_listener_tab") | n}
<br/>
<br/>

