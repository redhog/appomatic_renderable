import appomatic_renderable.models
import urllib
import django.http

def node(request, url):
    url = urllib.quote(url)
    if not url.startswith("/"): url = "/" + url
    nodes = appomatic_renderable.models.Node.objects.filter(url=url)
    if len(nodes):
        return django.http.HttpResponse(nodes[0].render(request))
    if url == "" or url == "/":
        return django.http.HttpResponse(appomatic_renderable.models.Node.list_render(request))
    else:
        raise Exception("Unknown path %s" % url)

def tag(request, url):
    url = urllib.quote(url)
    if not url.startswith("/"): url = "/" + url
    tags = appomatic_renderable.models.Tag.objects.filter(url=url)
    if len(tags):
        return django.http.HttpResponse(tags[0].render(request))
    if url == "" or url == "/":
        return django.http.HttpResponse(appomatic_renderable.models.Tag.render_list(request))
    else:
        raise Exception("Unknown tag path %s" % url)
