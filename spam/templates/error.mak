<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
                      "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">

<%namespace name="master" file="spam.templates.master"/>

<html xmlns="http://www.w3.org/1999/xhtml">
<head>
    <meta content="text/html; charset=UTF-8" http-equiv="content-type"/>
    <link rel="stylesheet" type="text/css" media="screen" href="${tg.url('/themes/%s/css/style.css' % c.theme)}" />
    <title>A ${code} Error has Occurred </title>
</head>

<body>
    ${master.header()}
    
    <div id="content">
        % if code==403:
            <div>${_('Access was denied to this resource.')}</div>
        %else:
            <div>${message | n}</div>
        % endif
    </div>
    
    ${master.footer()}
</body>
</html>

