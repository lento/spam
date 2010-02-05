## SPAM Spark Project & Asset Manager
##
## This program is free software; you can redistribute it and/or
## modify it under the terms of the GNU Lesser General Public
## License as published by the Free Software Foundation; either
## version 3 of the License, or (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
## Lesser General Public License for more details.
##
## You should have received a copy of the GNU Lesser General Public
## License along with this program; if not, write to the
## Free Software Foundation, Inc., 59 Temple Place - Suite 330,
## Boston, MA 02111-1307, USA.
##
## Original Copyright (c) 2010, Lorenzo Pierfederici <lpierfederici@gmail.com>
## Contributor(s): 
##

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

