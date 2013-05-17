import appomatic_renderable.models
import urllib
import django.http

def node(request, url):
    style = request.GET.get("style", "page.html")
    if '/' in style or style in (".", ".."): raise Exception("Bad style")
    if not url.startswith("/"): url = "/" + url
    nodes = appomatic_renderable.models.Node.objects.filter(url=url)
    if len(nodes):
        return django.http.HttpResponse(nodes[0].render(request, style=style))
    if url == "" or url == "/":
        return django.http.HttpResponse(appomatic_renderable.models.Node.render_list(request, style=style))
    else:
        raise Exception("Unknown path %s" % url)

def tag(request, name):
    style = request.GET.get("style", "page.html")
    if '/' in style or style in (".", ".."): raise Exception("Bad style")
    name=urllib.unquote_plus(name).decode('utf8')
    if name == "" or name == "/":
        return django.http.HttpResponse(appomatic_renderable.models.Tag.render_list(request, style=style))
    else:
        return django.http.HttpResponse(appomatic_renderable.models.Tag.objects.get(name=urllib.unquote_plus(name).decode('utf8')).render(request, style=style))
