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

