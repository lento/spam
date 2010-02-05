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

<%inherit file="spam.templates.master"/>

<script type="text/javascript">
    $(function() {
        $(".overlay").overlay(function() { 
            trigger = this.getTrigger();
            target = trigger.attr("href");
            iframe = $("#overlay iframe")[0];
            iframe.src = target
        });
    });
</script>

<div class="content">
    <a href="${tg.url('./new')}" rel="#overlay" class="overlay button">new project</a>
    <br/>
    <br/>
    <h1>${_('Active projects')}</h1>
    ${c.projects_active(id='projects_active', items=list(active)) | n}
    <br/>
    <br/>
    <h1>${_('Archived projects')}</h1>
    ${c.projects_archived(id='projects_archived', items=list(archived)) | n}
</div>

