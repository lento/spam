import re
from tw.api import Widget, WidgetsList, JSLink

def name2label(name):
    """
    Convert a column name to a Human Readable name.

    Stolen from tw.forms
    """
    # Create label from the name:
    #   1) Convert _ to spaces
    #   2) Convert CamelCase to Camel Case
    #   3) Upcase first character of Each Word
    # Note: I *think* it would be thread-safe to
    #       memoize this thing.
    return ' '.join([s.capitalize() for s in
               re.findall(r'([A-Z][a-z0-9]+|[a-z0-9]+|[A-Z0-9]+)', name)])


class LiveTable(Widget):
    params = ['id', 'items', 'show_headers', 'update_listener_adder',
              'update_topic', 'update_condition', 'update_functions',
              'extra_data']
    template = 'mako:spam.lib.twlib.livetable.templates.livetable'
    
    js_calls = []
    show_headers = False
    update_listener_adder = 'notify.add_listener'
    update_condition = 'true'
    update_functions = ('{"added": livetable.addrow,'
                        ' "deleted": livetable.deleterow,'
                        ' "updated": livetable.updaterow}'
                       )
    extra_data = {}
    
    def __new__(cls, id=None, parent=None, children=[], **kw):
        # add livetable javascripts to those defined by the subclassed widgets
        livetable_js = JSLink(modname='spam.lib.twlib.livetable',
                              filename='static/livetable.js')
        if livetable_js not in cls.javascript:
            cls.javascript.append(livetable_js)
        
        # get children widgets form the "field" keyword argument (if present)
        # or from the "fields" attribute (a WidgetList class containing widgets)
        fields = kw.pop('fields', None)
        if fields is not None:
            children = fields
        else:
            children = getattr(cls, 'fields', children)
        return super(LiveTable, cls).__new__(cls, id,parent,children,**kw)

    def __init__(self, *args, **kwargs):
        super(LiveTable, self).__init__(*args, **kwargs)
    
        # call javascript functions
        for call in self.js_calls:
            self.add_call(call)
    
    @property
    def ifields(self):
        return self.ifilter_children(lambda x: isinstance(x,TableData))

    def update_params(self,d):
        super(LiveTable, self).update_params(d)
        d['fields'] = list(self.ifields)


class TableData(Widget):
    params = ['field_class', 'show_header', 'sortable', 'sort_default',
              'sort_direction', 'condition']
    
    show_header = True
    sortable = True
    sort_default = False
    sort_direction = 'asc'
    condition = 'true'


class IconButton(TableData):
    params = ['label_text', 'icon_class', 'action']
    template = 'mako:spam.lib.twlib.livetable.templates.icon_button'
    
    field_class = 'icon'
    show_header = False
    sortable = False
    
    def __init__(self, id=None, parent=None, children=[], **kw):
        super(IconButton, self).__init__(id,parent,children, **kw)
        if self.label_text is None and self.id is not None:
            self.label_text = name2label(id)


class IconBox(TableData):
    template = 'mako:spam.lib.twlib.livetable.templates.icon_box'
    
    field_class = 'iconbox'

    def __new__(cls, id=None, parent=None, children=[], **kw):
        # get children widgets form the "buttons" keyword argument (if present)
        # or from the "buttons" attribute (a WidgetList containing widgets)
        buttons = kw.pop('buttons', None)
        if buttons is not None:
            children = buttons
        else:
            children = getattr(cls, 'buttons', children)
        return super(IconBox, cls).__new__(cls, id,parent,children,**kw)

    @property
    def ibuttons(self):
        return self.ifilter_children(lambda x: isinstance(x,IconButton))

    def update_params(self,d):
        super(IconBox, self).update_params(d)
        d['buttons'] = list(self.ibuttons)


class TextData(TableData):
    template = 'mako:spam.lib.twlib.livetable.templates.text_data'
    
    field_class = 'text'


class LinkData(TableData):
    params = ['dest']
    template = 'mako:spam.lib.twlib.livetable.templates.link_data'
    
    field_class = 'link'


class ThumbData(TableData):
    params = ['src', 'dest']
    template = 'mako:spam.lib.twlib.livetable.templates.thumb_data'
    
    field_class = 'thumbnail'
    

