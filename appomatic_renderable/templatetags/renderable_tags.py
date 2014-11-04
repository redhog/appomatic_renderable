import django.template
from fcdjangoutils.timer import Timer 

register = django.template.Library()

class RenderNode(django.template.Node):
    def __init__(self, **kw):
        self.vars = {
            key: django.template.Variable(value)
            for key, value in kw.iteritems()
            }

    def render(self, context):
        vars = {
            key: value.resolve(context)
            for key, value in
            self.vars.iteritems()
            }
        obj = vars.pop("obj")
        args = {'context_arg': vars}
        if 'style' in vars: args['style'] = vars.pop("style")
        return obj.render(**args)

@register.tag
def render(parser, token):
    tokens = dict(item.split("=", 1)
                  for item in token.split_contents()[1:])
    return RenderNode(**tokens)
