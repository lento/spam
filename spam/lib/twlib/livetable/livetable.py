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
    params = ['id', 'items']
    template = 'mako:spam.lib.twlib.livetable.templates.livetable'
    live_table_js = JSLink(modname='spam.lib.twlib.livetable', filename='static/livetable.js')
    javascript=[live_table_js]

    def __new__(cls, id=None, parent=None, children=[], **kw):
        fields = kw.pop('fields', None)
        if fields is not None:
            children = fields
        else:
            children = getattr(cls, 'fields', children)
        return super(LiveTable, cls).__new__(cls, id,parent,children,**kw)

    @property
    def ifields(self):
        return self.ifilter_children(lambda x: isinstance(x,TableField))

    def update_params(self,d):
        super(LiveTable, self).update_params(d)
        d['fields'] = list(self.ifields)


class TableField(Widget):
    params = ['field_class']


class IconButton(TableField):
    template = 'mako:spam.lib.twlib.livetable.templates.icon_button'
    params = ['label_text', 'icon_class']
    
    field_class = 'icon'
    
    def __init__(self, id=None, parent=None, children=[], **kw):
        super(IconButton, self).__init__(id,parent,children, **kw)
        if self.label_text is None and self.id is not None:
            self.label_text = name2label(id)


class TextField(TableField):
    template = 'mako:spam.lib.twlib.livetable.templates.text_field'
    
    field_class = 'text'


