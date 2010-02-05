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

<%inherit file="spam.templates.standalone"/>

<%def name="style()">
    <link rel="stylesheet" type="text/css" media="screen" href="${tg.url('/themes/%s/css/form.css' % c.theme)}" />
</%def>

<script type="text/javascript">
    $(function() {
        $("label", $("input:disabled").parent()).addClass('disabled');
    });
</script>

<h1>${title}</h1>
    % if msg:
        <div class="msg">${msg}</div>
    % endif
    % if warning:
        <div class="warning">${warning}</div>
    % endif
    ${c.form(args, child_args=child_args) | n}

