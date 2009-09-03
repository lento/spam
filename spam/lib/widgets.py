import tg
from tw.api import Widget
from tw.api import JSLink

spam_js = JSLink(link=tg.url('/parsedjs/spam.js'))

# JQuery and plugins
jquery_js = JSLink(link=tg.url('/js/jquery.js'))


class StartupJS(Widget):
    javascript = [jquery_js, spam_js]


