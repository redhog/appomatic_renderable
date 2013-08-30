import ckeditor.fields
import mptt.models
import fcdjangoutils.modelhelpers
import fcdjangoutils.middleware
import fcdjangoutils.fields
import fcdjangoutils.jsonview
import datetime
import django.template
import django.utils.http
import django.contrib.auth.models
import django.core.urlresolvers
import django.db.models
import django.db.models.fields.related
import django.utils.functional
import django.db.models.query
import django.utils.html
from django.db.models import Q
from django.conf import settings
import csv
import StringIO
import urllib

def get_typename(t, separator = "."):
    return ("%s.%s" % (t.__module__, t.__name__)).replace(".", separator)

def get_basetypes(t, separator = "."):
    basetypes = []
    def get_basetypes(t):
        basetypes.append(get_typename(t))
        for tt in t.__bases__:
            get_basetypes(tt)
    get_basetypes(t)
    return basetypes

TypeType = type

class Renderable(fcdjangoutils.modelhelpers.SubclasModelMixin):
    @fcdjangoutils.modelhelpers.subclassproxy
    def get_admin_url(self):
        return django.core.urlresolvers.reverse(
            'admin:%s_%s_change' % (self._meta.app_label,
                                    self._meta.module_name),
            args=[self.id])

    @fcdjangoutils.modelhelpers.subclassproxy
    @property
    def types(self):
        return ' '.join(get_basetypes(TypeType(self), "-"))

    @fcdjangoutils.modelhelpers.subclassproxy
    @property
    def type(self):
        return get_typename(TypeType(self), "-")

    @fcdjangoutils.modelhelpers.subclassproxy
    @property
    def type_name(self):
        return TypeType(self).__name__

    @fcdjangoutils.modelhelpers.subclassproxy
    def render_as(self):
        obj = self
        class Res(object):
            def __getattribute__(self, style):
                style = style.replace("__", ".")
                if "." not in style: style = style + ".html"
                return obj.render(fcdjangoutils.middleware.get_request(), style)
        return Res()

    def context(self, request, style):
        return {'obj': self.subclassobject}

    def handle_methods(self, request, style):
        method = 'handle__' + request.REQUEST.get('method', 'read')
        if hasattr(self, method):
            return getattr(self, method)(request, style)
        else:
            return {}

    @fcdjangoutils.modelhelpers.subclassproxy
    def render(self, request, style = None, context_arg = {}, as_response = False):
        if style is None:
            style = request.GET.get("style", "page.html")
            if '/' in style or style in (".", ".."): raise Exception("Bad style")
        subtype = ''
        if hasattr(self, 'render_subtype'):
            subtype = "/" + self.render_subtype
        context = self.context(request, style)
        context.update(self.handle_methods(request, style))
        context.update(context_arg)

        method = 'render__' + style.replace(".", "__")
        if hasattr(self, method):
            res = getattr(self, method)(request, context)
        else:
            res = django.template.loader.select_template(
                ["%s%s/%s" % (t.replace(".", "/"), subtype, style)
                 for t in get_basetypes(type(self))]
                ).render(
                django.template.RequestContext(
                        request,
                        context))

        # res can be either string or HttpResponse object. We might
        # need either. So, convert as required...

        if isinstance(res, django.http.HttpResponse):
            if not as_response:
                res = res.content
        else:
            if as_response:
                res = django.http.HttpResponse(res)

        return res

    def render__adminlink__html(self, request, context):
        # Handle translation here
        return u"<a href='%s'>Edit</a>" % (self.get_admin_url(),)

    def render__link__html(self, request, context):
        return u"<a href='%s'>%s</a>" % (self.get_absolute_url(), self)

    def render__oembedlink__html(self, request, context):
        return u"""
          <link rel='alternate' type='application/json+oembed' href='%(url)s?style=oembed&format=json' title='%(title)s' />
          <link rel='alternate' type='text/xml+oembed' href='%(url)s?style=oembed&format=xml' title='%(title)s' />
        """ % {
            'url': self.get_absolute_url() + "",
            'title': self}

    def render__oembed(self, request, context):
        format = request.GET.get('format', 'json')
        data = self.oembed(request, context)
        if format == 'json':
            return fcdjangoutils.jsonview.to_json(data)
        elif format == 'xml':
            return '<?xml version="1.0" encoding="utf-8" standalone="yes"?><oembed>%s</oembed>' % ('\n'.join(
                    '<%(key)s>%(value)s</%(key)s>' % {'key':key, 'value':django.utils.html.escape(unicode(value).encode('utf-8'))}
                    for (key, value) in data.iteritems()),)
        else:
            raise Exception("Unknown format %s" % (format,))

    oembedwidth = 400
    oembedheight = 300

    def oembed(self, request, context):
        return {
            'type': 'rich',
            'version': 1.0,
            "provider_url": request.build_absolute_uri('/')[:-1],
            'html': self.render(request, 'excerpt.html'),
            'width': self.oembedwidth,
            'height': self.oembedheight
            }

    @classmethod
    def list_context(cls, request, style):
        return {"objs": cls.objects.all()}

    @classmethod
    def list_handle_methods(cls, request, style):
        method = 'list_handle__' + request.REQUEST.get('method', 'read')
        if hasattr(cls, method):
            return getattr(cls, method)(request, style)
        else:
            return {}

    @classmethod
    def list_render(cls, request, style = None, context_arg = {}, as_response = False):
        if style is None:
            style = request.GET.get("style", "page.html")
            if '/' in style or style in (".", ".."): raise Exception("Bad style")
        subtype = ''
        if hasattr(cls, 'render_subtype'):
            subtype = "/" + cls.render_subtype
        context = cls.list_context(request, style)
        context.update(cls.list_handle_methods(request, style))
        context.update(context_arg)

        method = 'list_render__' + style.replace(".", "__")
        if hasattr(cls, method):
            res = getattr(cls, method)(request, context)
        else:
            res = django.template.loader.select_template(
                ["%s-list/%s" % (t.replace(".", "/"), style)
                 for t in get_basetypes(cls)]
                ).render(
                django.template.RequestContext(
                        request,
                        context))

        # res can be either string or HttpResponse object. We might
        # need either. So, convert as required...

        if isinstance(res, django.http.HttpResponse):
            if not as_response:
                res = res.content
        else:
            if as_response:
                res = django.http.HttpResponse(res)

        return res

    @classmethod
    def list_render__csv(cls, request, context):
        f = StringIO.StringIO()
        w = csv.writer(f)
        header = None
        for row in context['objs'].values():
            if header is None:
                header = row.keys()
                header.sort()
                w.writerow(header)
            w.writerow([row[col] for col in header])
        return f.getvalue()

class Tag(mptt.models.MPTTModel, Renderable):
    name = django.db.models.CharField(max_length=128)
    parent = mptt.models.TreeForeignKey('self', null=True, blank=True, related_name='children')
    url = django.db.models.CharField(max_length=1024, null=True, blank=True, unique=True)

    def save(self, *arg, **kw):
        if self.parent:
            self.url = '/'.join(self.parent.url.split("/") + [urllib.quote(self.name.encode("utf-8"))])
        else:
            self.url = '/' + urllib.quote(self.name.encode("utf-8"))
        mptt.models.MPTTModel.save(self, *arg, **kw)

    @property
    def pure_children(self):
        return self.children.annotate(node_nr=django.db.models.Count('node')).filter(node_nr=0)

    class Meta:
        unique_together = (("name", "parent"),)
        ordering = ('name', )        

    class MPTTMeta:
        order_insertion_by = ['name']

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        nodes = Node.objects.filter(title = self.name)
        if len(nodes):
            return nodes[0].get_absolute_url()
        else:
            return django.core.urlresolvers.reverse('appomatic_renderable.views.tag', kwargs={'url': urllib.unquote(self.url)})

    def breadcrumb(self, include_self=False):
        return self.get_ancestors(include_self=include_self)

    @classmethod
    def list_context(cls, request, style):
        return {"objs": cls.objects.filter(parent = None)}

    @classmethod
    def menutree(cls):
        def menutree(parent = None):
            if parent:
                children = parent.pure_children.all()
            else:
                children = cls.objects.filter(parent=None)
            if len(children) == 0:
                return ""
            else:
                csscls = ["menu"]
                if parent is None: csscls.append("menubar")
                items = ""
                if parent is None:
                    items = "<li><a href='/'>Home</a></li>"
                items += "\n".join("<li><a href='%s'>%s</a>%s</li>" % (child.get_absolute_url(),
                                                                       child.name,
                                                                       menutree(child))
                                   for child in children)
                return "<ul class='%s'>%s</ul>" % (
                    " ".join(csscls),
                    items)
        if not getattr(cls, "_menutree", None):
            cls._menutree = menutree()
        return cls._menutree

    def oembed(self, request, context):
        res = Renderable.oembed(self, request, context)
        res.update({
                'title': self.name,
                })
        return res

class Source(django.db.models.Model):
    tool = django.db.models.CharField(max_length=50)
    argument = django.db.models.CharField(max_length=1024)

    def __unicode__(self):
        return "%s: %s" % (self.tool, self.argument)

class License(django.db.models.Model):
    name = django.db.models.CharField(max_length=50)
    url = django.db.models.CharField(max_length=1024)

    def __unicode__(self):
        return "<a href='%s'>%s</a>" % (self.url, self.name)

class Node(django.db.models.Model, Renderable):
    url = django.db.models.CharField(max_length=1024, unique=True)
    tags = django.db.models.ManyToManyField(Tag, null=True, blank=True, related_name='nodes')
    title = django.db.models.CharField(max_length=128, db_index=True)
    published = django.db.models.DateTimeField(default=datetime.datetime.now, null=True, blank=True, db_index=True)
    source = django.db.models.ForeignKey(Source, null=True, blank=True)
    license = django.db.models.ForeignKey(License, null=True, blank=True)
    author = django.db.models.ForeignKey(django.contrib.auth.models.User, null=True, blank=True)

    tag = fcdjangoutils.fields.WeakForeignKey(from_field="title", to=Tag, to_field="name", related_name="node")

    @fcdjangoutils.modelhelpers.subclassproxy
    def __unicode__(self):
        return self.title

    def get_absolute_url(self):
        return django.core.urlresolvers.reverse('appomatic_renderable.views.node', kwargs={'url': self.url[1:]})

    def breadcrumb(self):
        #if self.tag:
        #    return self.tag.get().breadcrumb()
        tags = self.tags.all()
        if len(tags):
            return tags[0].breadcrumb(include_self=True)
        return []

    class Meta:
        ordering = ('-published', 'title', )

    @classmethod
    def get(cls):
        Obj = cls
        class Res(object):
            def __getattribute__(self, url):
                return Obj.objects.get(url = "/" + url.replace("__", "/"))
        return Res()

    @classmethod
    def list_context(cls, request, style):
        return {"objs": cls.objects.filter(~Q(published=None))}

    def oembed(self, request, context):
        res = Renderable.oembed(self, request, context)
        res.update({
                'title': self.title,
                'author_name': "%s (%s)" % (self.author.username, self.author.get_full_name()),
                'author_url': self.author.get_absolute_url()
                })
        return res


class Collection(Node):
    @fcdjangoutils.modelhelpers.subclassproxy
    def items(self):
        return []

class ListCollection(Collection):
    nodes = django.db.models.ManyToManyField(Node, null=True, blank=True, through='ListCollectionMember', related_name='in_list_collection')
    
    def items(self):
        relations = ListCollectionMember.objects.filter(collection = self)

        return Node.objects.filter(
            member_in_list_collection__in = relations
            ).annotate(
            ordering = django.db.models.Min('member_in_list_collection__ordering')
            ).order_by('ordering').distinct()

class ListCollectionMember(django.db.models.Model):
    collection = django.db.models.ForeignKey(ListCollection, related_name="members")
    node = django.db.models.ForeignKey(Node, related_name='member_in_list_collection')
    ordering = django.db.models.FloatField(default = 0)    

class Article(Node):
    summary = ckeditor.fields.RichTextField(blank=True, null=True)
    content = ckeditor.fields.RichTextField()
    extra = ckeditor.fields.RichTextField(null=True, blank=True)
    image = django.db.models.ForeignKey(Node, null=True, blank=True, related_name="image_for")

class File(Node):
    content = django.db.models.FileField(max_length=2048, upload_to='.')
    description = ckeditor.fields.RichTextField(blank=True, null=True)

class Image(Node):
    content = django.db.models.ImageField(max_length=2048, upload_to='.')
    description = ckeditor.fields.RichTextField(blank=True, null=True)

    def oembed(self, request, context):
        return {
            'type': 'photo',
            'version': 1.0,
            "provider_url": request.build_absolute_uri('/')[:-1],
            'url': self.content.url,
            'width': self.content.width,
            'height': self.content.height,
            'title': self.title,
            'author_name': "%s (%s)" % (self.author.username, self.author.get_full_name()),
            'author_url': self.author.get_absolute_url()
            }

class StaticTemplate(Node):
    render_subtype = django.db.models.CharField(
        max_length=50,
        choices=(
            ('MainMenu', 'Main menu'),
            ('Badge/FaceBook', 'FaceBook badge'),
            ('Badge/GitHub', 'GitHub badge'),
            ('Badge/Twitter', 'Twitter badge'),
            ('Badge/Twingly', 'Twingly badge'),
            ('Badge/LinkedIn', 'LinkedIn badge')
            ))
