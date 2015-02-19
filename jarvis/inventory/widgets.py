from django.forms.widgets import Input
from django.utils.html import format_html
from django.forms.util import flatatt
from django.utils.safestring import mark_safe

class DictFieldWidget(Input):
    input_type = "text"
    table_attrs = {"class":"jarv-attr-edit-table"}
    key_attrs = {"class":"item-attr-key"}
    val_attrs = {"class":"item-attr-value"}

    def render(self, name, value, attrs=None):
        if value is None: 
            value = ''
        final_attrs = self.build_attrs(attrs, name=name)
        output = [format_html('<table{0}>', flatatt(final_attrs))]
        
        pairs = self.render_pairs(value)
        if pairs:
            output.append(pairs)
        
        output.append('</table>')
        return mark_safe('\n'.join(output))

    def render_pairs(self, value):
        output = []
        for key, val in value.iteritems():
            output.append(self.render_pair(key, value))
        return '\n'.join(output)

    def render_pair(self, key, value):
        output = []
        output.append(format_html('<input type="{0}" name="{1}" value="{2}"{3}/>', 
                self.input_type,
                (key + "-key"),
                key,
                self.key_attrs
        ))

        output.append(format_html('<input type="{0}" name="{1}" value="{2}"{3}/>',
                    self.input_type,
                    (key + "-value"),
                    value,
                    self.val_attrs))
        return '\n'.join(output)
