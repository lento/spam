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

<%namespace name="sidebars" file="spam.templates.sidebars"/>


<html xmlns="http://www.w3.org/1999/xhtml">
<head>
    <!-- document.domain is needed by orbited for cross-port deployment
    <script> document.domain = document.domain; </script>-->
    ${self.meta()}
    <title>${self.title()}</title>
    <link rel="stylesheet" type="text/css" media="screen" href="${tg.url('/themes/%s/css/style.css' % c.theme)}" />

    <script type="text/javascript">
    $(function() {
        spam_init("${tg.url('/')}");
        spam.sidebar_set_active("${sidebar and sidebar[0] or ''}",
                                "${sidebar and sidebar[1] or ''}");

        notify_init("${tg.config.get('stomp_host', 'localhost')}",
                    ${tg.config.get('stomp_port', '61613')});
    });
    </script>
</head>

<body>
    <div id="overlay">
        <div class="wrap"></div>
        <iframe src="about:blank"></iframe>
    </div>

    ${self.header()}
    ${self.flash_wrapper()}

    <div id="side">
    % if request.identity:
        <div id="side_fixed" class="side">
            ${sidebars.sb_admin()}
            ${sidebars.sb_user()}
            ${sidebars.sb_projects()}
        </div>
        % if hasattr(c, 'project') and c.project:
            <div id="side_overflow_container">
                <div id="side_overflow_activearea">
                    <div id="side_overflow" class="side overflow">
                        ${sidebars.sb_project()}
                    </div>
                </div>
            </div>
        % endif
    % endif
    </div>

    ${self.content_wrapper()}
    ${self.footer()}
</body>


<%def name="meta()">
  <meta content="text/html; charset=UTF-8" http-equiv="content-type"/>
</%def>


<%def name="title()">
    % if page:
        SPAM - ${page}
    % else:
        SPAM
    % endif
</%def>


<%def name="header()">
    <div id="header">
        <a class="logo" href="${tg.url('/')}"></a>
  	    
        % if request.identity is None:
            <a class="login button" href="${tg.url('/login')}">login</a>
        % else:
            <a class="logout button" href="${tg.url('/logout_handler')}">logout</a>
            <div class="username" py:content="c.user.user_name">${c.user.user_name}</div>
        % endif
        
  	    <div class="title">
  	    	% if hasattr(c, 'project') and c.project:
  	    	    ${c.project.name}
    	    % else:
    	        SPAM
	        % endif
	    </div>
        % if page:
            <div class="path">${page}</div>
        % endif
    </div>
</%def>


<%def name="flash_wrapper()">
    <%
    flash=tg.flash_obj.render('flash', use_js=False)
    %>
    % if flash:
        ${flash | n}
    % endif
</%def>


<%def name="content_wrapper()">
    <div id="content_wrapper">
        ${self.body()}
    </div>
</%def>


<%def name="footer()">
    <div id="footer"> 
        <a class="flogo" href="http://www.turbogears.org/2.0/"></a>
        <div class="foottext">Copyright (c) 2008-2009</div>
    </div>
</%def>


</html>
