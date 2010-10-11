## This file is part of SPAM (Spark Project & Asset Manager).
##
## SPAM is free software: you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
##
## SPAM is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with SPAM.  If not, see <http://www.gnu.org/licenses/>.
##
## Original Copyright (c) 2010, Lorenzo Pierfederici <lpierfederici@gmail.com>
## Contributor(s): 
##

<%def name="insert_libgroup(libgroup)">
    <li id="${libgroup.id}">
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


<div id="sb_project_tree" class="hidden">
    <ul>
        <li id="scenes">
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
                    <li id="${scene.id}">
                        <a href="${tg.url('/scene/%s/%s/' % (c.project.id, scene.name))}">
                            ${scene.name}
                        </a>
                        % if scene.shots:
                            <ul>
                                % for shot in scene.shots:
                                <li id="${shot.id}">
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
        <li id="library">
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
</div>

<script type="text/javascript">
    $.jstree._themes = "${tg.url('/themes/%s/jstree/' % c.theme)}";
    $("#sb_project_tree").jstree({
        "core": {
            "animation": 100,
        },
		"themes" : {
			"theme" : "default",
			"dots" : true,
			"icons" : false
		},
        "plugins" : [ "themes", "html_data", "cookies" ],
        "cookies" : {
            "cookie_options" : {
                "path" : "${url('/')}"
                },
            "save_opened" : "spam_jstree_${c.project.id}"
        }
    }).show();
</script>

