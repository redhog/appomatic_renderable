import appomatic_renderable.models
import django.contrib.admin
import mptt.admin
import autocomplete.widgets
import fcdjangoutils.fields

class TagAdmin(mptt.admin.MPTTModelAdmin):
    exclude = ('url',)
django.contrib.admin.site.register(appomatic_renderable.models.Tag, TagAdmin)
class NodeAdmin(autocomplete.widgets.AutocompleteModelAdmin):
    # exclude = ('tag',)
    list_display = ('published', 'title', 'source', 'license', 'author', 'url')
    list_display_links = ('published', 'title', 'source', 'license', 'author', 'url')
    list_filter = ('source', 'license', 'author')
    search_fields = ('title', 'source__tool', 'license__name', 'author__username', 'author__first_name', 'author__last_name', 'url')
    date_hierarchy = 'published'
    related_search_fields = {'tags': ('name',)}
django.contrib.admin.site.register(appomatic_renderable.models.Source)
class ArticleAdmin(NodeAdmin):
    related_search_fields = {'tags': ('name',),
                             'image': ('title',)}
django.contrib.admin.site.register(appomatic_renderable.models.Article, ArticleAdmin)
django.contrib.admin.site.register(appomatic_renderable.models.File, NodeAdmin)
django.contrib.admin.site.register(appomatic_renderable.models.Image, NodeAdmin)

class ListCollectionMemberInline(autocomplete.widgets.AutocompleteTabularInline):
    model = appomatic_renderable.models.ListCollectionMember
    fk_name = "collection"
    related_search_fields = {'node': ('title',)}

class ListCollectionAdmin(NodeAdmin):
    inlines = [ListCollectionMemberInline]

django.contrib.admin.site.register(appomatic_renderable.models.ListCollection, ListCollectionAdmin)

django.contrib.admin.site.register(appomatic_renderable.models.StaticTemplate, NodeAdmin)
