<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" 
                      "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">

<html xmlns="http://www.w3.org/1999/xhtml">

<head>
    <meta content="text/html; charset=UTF-8" http-equiv="content-type"/>
    ${self.style()}
</head>
${c.startupjs()}

<body>
    ${self.body()}
</body>

</html>

<%def name="style()">
    <link rel="stylesheet" type="text/css" media="screen" href="${tg.url('/themes/%s/css/style.css' % c.theme)}" />
</%def>

