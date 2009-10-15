<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" 
                      "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">

<html xmlns="http://www.w3.org/1999/xhtml">

<head>
    <meta content="text/html; charset=UTF-8" http-equiv="content-type"/>
    <link rel="stylesheet" type="text/css" media="screen" href="${tg.url('/themes/%s/css/form.css' % c.theme)}" />
    <script type="text/javascript" src="/spam/js/jquery.js"></script>
    <script type="text/javascript">
        $(function() {
            $("label", $("input:disabled").parent()).addClass('disabled');
        });
    </script>

</head>

<body>
    <h1>${title}</h1>
    ${c.form(args, child_args=child_args) | n}
</body>

</html>

