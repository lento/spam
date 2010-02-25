<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
                      "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">

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

<%namespace name="master" file="spam.templates.master"/>

<html xmlns="http://www.w3.org/1999/xhtml">
<head>
    <meta content="text/html; charset=UTF-8" http-equiv="content-type"/>
    <link rel="stylesheet" type="text/css" media="screen" href="${tg.url('/themes/%s/css/style.css' % c.theme)}" />
    <title>A ${code} Error has Occurred </title>
</head>

<body>
    ${master.header()}
    
    <div id="content_wrapper">
        <div class="content">
            % if code==403:
                <div>${_('Access was denied to this resource.')}</div>
            %else:
                <div>${message | n}</div>
            % endif
        </div>
    </div>
    
    ${master.footer()}
</body>
</html>

