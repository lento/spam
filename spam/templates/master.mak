<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
                      "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">

<%namespace name="sidebars" file="spam.templates.sidebars"/>


<html>
<head>
    ${self.meta()}
    <title>${self.title()}</title>
    <link rel="stylesheet" type="text/css" media="screen" href="${tg.url('/themes/%s/css/style.css' % c.theme)}" />

    ##${c.startupjs()}
</head>
<body>
    ${self.header()}
    ${self.flash_wrapper()}

    % if request.identity:
    <div id="side">
        ${sidebars.admin()}
        ${sidebars.user()}
        ${sidebars.projects()}
    </div>
    % endif

    ${self.content_wrapper()}
    ${self.footer()}
</body>

<%def name="meta()">
  <meta content="text/html; charset=UTF-8" http-equiv="content-type"/>
</%def>


<%def name="title()">  </%def>


<%def name="header()">
    <div id="header">
        <a class="logo" href="${tg.url('/')}"></a>
  	    
        % if request.identity is None:
            <a class="login button" href="${tg.url('/login')}">login</a>
        % else:
            <a class="logout button" href="${tg.url('/logout_handler')}">logout</a>
            <div class="username" py:content="c.user.user_name">username</div>
        % endif
        
  	    <div class="title">
  	    	Nome del Progetto
	    </div>
        % if page:
            <div class="path">${page}</div>
        % endif
    </div>
</%def>


<%def name="sidebar_top()">
  <div id="sb_top" class="sidebar">
      <h2>Get Started with TG2</h2>
      <ul class="links">
        <li>
          % if page == 'index':
              <span><a href="${tg.url('/about')}">About this page</a> A quick guide to this TG2 site </span>
          % else:
              <span><a href="${tg.url('/')}">Home</a> Back to your Quickstart Home page </span>
          % endif
        </li>
        <li><a href="http://www.turbogears.org/2.0/docs/">TG2 Documents</a> - Read everything in the Getting Started section</li>
        <li><a href="http://docs.turbogears.org/1.0">TG1 docs</a> (still useful, although a lot has changed for TG2) </li>
        <li><a href="http://groups.google.com/group/turbogears"> Join the TG Mail List</a> for general TG use/topics  </li>
      </ul>
  </div>
</%def>

<%def name="sidebar_bottom()">
  <div id="sb_bottom" class="sidebar">
      <h2>Developing TG2</h2>
      <ul class="links">
        <li><a href="http://docs.turbogears.org/2.0/RoughDocs/">More TG2 Documents</a> in progress</li>
        <li><a href="http://trac.turbogears.org/query?status=new&amp;status=assigned&amp;status=reopened&amp;group=type&amp;milestone=2.0&amp;order=priority">TG2 Trac tickets</a> What's happening now in TG2 development</li>
        <li><a href="http://trac.turbogears.org/timeline">TG Dev timeline</a> (recent ticket updates, svn checkins, wiki changes)</li>
        <li><a href="http://svn.turbogears.org/trunk">TG2 SVN repository</a> For checking out a copy</li>
        <li><a href="http://turbogears.org/2.0/docs/main/Contributing.html#installing-the-development-version-of-turbogears-2-from-source">Follow these instructions</a> For installing your copy</li>
        <li><a href="http://trac.turbogears.org/browser/trunk">TG2 Trac's svn view</a> In case you need a quick look</li>
        <li><a href="http://groups.google.com/group/turbogears-trunk"> Join the TG-Trunk Mail List</a> for TG2 discuss/dev </li>
      </ul>
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
    <div id="content">
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
