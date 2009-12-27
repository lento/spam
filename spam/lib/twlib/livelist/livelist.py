from tw.api import Widget, WidgetsList, JSLink

class LiveList(Widget):
    params = ['id', 'items', 'update_listener_adder', 'extra_data',
              'update_topic', 'update_condition', 'update_functions',
             ]
    template = 'mako:spam.lib.twlib.livelist.templates.livelist'
    
    js_calls = []
    update_listener_adder = 'notify.add_listener'
    update_condition = 'true'
    update_functions = ('{"added": livelist.additem,'
                        ' "deleted": livelist.deleteitem,'
                        ' "updated": livelist.updateitem}'
                       )
    extra_data = {}
    
    def __new__(cls, id=None, parent=None, children=[], **kw):
        # add livelist javascripts to those defined by the subclassed widgets
        livelist_js = JSLink(modname='spam.lib.twlib.livelist',
                              filename='static/livelist.js')
        if livelist_js not in cls.javascript:
            cls.javascript.append(livelist_js)
        
        # get children widgets form the "field" keyword argument (if present)
        # or from the "fields" attribute (a WidgetList class containing widgets)
        fields = kw.pop('fields', None)
        if fields is not None:
            children = fields
        else:
            children = getattr(cls, 'fields', children)
        return super(LiveList, cls).__new__(cls, id,parent,children,**kw)

    def __init__(self, *args, **kwargs):
        super(LiveList, self).__init__(*args, **kwargs)
    
        # call javascript functions
        for call in self.js_calls:
            self.add_call(call)
    
    @property
    def ifields(self):
        return self.ifilter_children(lambda x: isinstance(x,ListItem))

    def update_params(self,d):
        super(LiveList, self).update_params(d)
        d['fields'] = list(self.ifields)


class ListItem(Widget):
    params = ['field_class', 'condition']
    
    condition = 'true'


class TextItem(ListItem):
    template = 'mako:spam.lib.twlib.livelist.templates.text_item'
    
    field_class = 'text'


class LinkItem(ListItem):
    params = ['dest']
    template = 'mako:spam.lib.twlib.livelist.templates.link_item'
    
    field_class = 'link'



