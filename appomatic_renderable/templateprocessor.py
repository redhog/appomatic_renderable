import appomatic_renderable.models

def defaults(request):
    return {"Tag":appomatic_renderable.models.Tag,
            "Node":appomatic_renderable.models.Node}
