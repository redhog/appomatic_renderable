# About

A mini cms framework to make django models easily "renderable" using templates


# Mini-tutorial
# Preparing the models
Add the mixin appomatic_renderable.models.Renderable to the superclasses of your model.

# Usage in templates

    {{somemodelobject.render_as.excerpt|safe}}

This will use the type of the object (and its base classes) together
with the style "excerpt" (you can use any string here), to determine
what template to use to render the object. The template will be run,
with the object bound to the template variable "obj", and the result
will be returned (and inserted in the current template).

If for example somemodelobject if of class
appomatic_myapp.models.MyModel which inherits from
appomatic_websitebase.models.BaseModel, then the following templates
will be searched for (in this order, the first one found will be
used):

    appomatic_myapp/models/MyModel/excerpt.html
    appomatic_websitebase/models/BaseModel/excerpt.html

The .html is added, unless you specify something else:

    {{somemodelobject.render_as.excerpt__txt|safe}}

will use the templates

    appomatic_myapp/models/MyModel/excerpt.txt
    appomatic_websitebase/models/BaseModel/excerpt.txt

# Built in styles

* link__html

  Generates a link (a href) to the object using unicode(obj) to
  generate the link title, and obj.get_absolute_url() to generate the
  url

* adminlink__html

  Generates a link to the django admin page for editing this object,
  using obj.get_admin_url().

* oembedlink__html

  Generates proper html tags linking to an oembed provider for this
  object.

* oembed

  Generates oembed data for your object. Uses the query parameter
  "format" to determine if it is to generate cml or json oembed data,
  default is json.


# Views

For models inheriting from either appomatic_renderable.models.Tag or
appomatic_renderable.models.Node a url is provided, resolving to a
view that renders the object using the same logic as the template tag,
using the style "page.html" (by default, the style can be overridden
using a query parameter "style").


# Lists 

There is also a list rendering mode, which uses the same template
template lookup mechanism as the instance renderer, but with "-list"
appended to the class name, e.g.

    appomatic_renderable/models/Node-list/page.html

This is made available for Tag:s and Node:s under the urls /tag/ and
/node/ respectively.
