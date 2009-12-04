<%def name="insert_libgroup(libgroup)">
    <li>
        <a href="${tg.url('/libgroup/%s/%s/' % (c.project.id, libgroup.id))}">
            ${libgroup.name}
        </a>
        % if libgroup.subgroups:
            <ul>
                % for subgroup in libgroup.subgroups:
                    ${insert_libgroup(subgroup)}
                % endfor
            </ul>
        % endif
    </li>
</%def>    


${c.j_notify_client()}
<div class="title">
    <a href="${tg.url('/project/%s' % c.project.id)}">${c.project.name}</a>
</div>
<ul id="sb_project_tree" class="hidden">
    <li>
        <%
            tab_scenes_url = tg.url('/scene/%s' % c.project.id)
            scenes_url = tg.url('/project/%s/#%s' % (c.project.id, tab_scenes_url))
            tab_library_url = tg.url('/libgroup/%s' % c.project.id)
            library_url = tg.url('/project/%s/#%s' % (c.project.id, tab_library_url))
        %>
        <a href="${scenes_url}">scenes</a>
        % if c.project.scenes:
            <ul id="sb_project_scenes">
                % for scene in c.project.scenes:
                <li>
                    <a href="${tg.url('/scene/%s/%s/' % (c.project.id, scene.name))}">
                        ${scene.name}
                    </a>
                    % if scene.shots:
                        <ul>
                            % for shot in scene.shots:
                            <li>
                                <a href="${tg.url('/shot/%s/%s/%s/' % (c.project.id, scene.name, shot.name))}">
                                    ${shot.name}
                                </a>
                            </li>
                            % endfor
                        </ul>
                    % endif
                </li>
                % endfor
            </ul>
        % endif
    </li>
    <li>
        <a href="${library_url}">library</a>
        % if c.project.libgroups:
            <ul id="sb_project_libgroups">
                % for libgroup in c.project.libgroups:
                    ${insert_libgroup(libgroup)}
                % endfor
            </ul>
        % endif
    </li>
</ul>

<script type="text/javascript">
    $("#sb_project_tree").treeview({
        persist: "cookie",
        cookieId: "project_treeview",
        cookieOptions: {path: "${tg.url('/')}"},
        collapsed: true
    }).show();
</script>

