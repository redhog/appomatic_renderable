import django.conf.urls

urlpatterns = django.conf.urls.patterns('',
    (r'^tag(?P<url>.*)/?$', 'appomatic_renderable.views.tag'),
    (r'^node(?P<url>.*)/?$', 'appomatic_renderable.views.node'),
)
