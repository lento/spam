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

<script type="text/javascript">
    $(function() {
        $("#uploader").uploader({target: "${target}",
                                 queue: "${queue}",
                                 submitter: "${submitter}",
                                 ext: "${ext}"});
    });
</script>

<input id="uploader" name="${id}" type="file" multiple="true" id="input" />
<br/>
<div id="upload_queue"></div>

