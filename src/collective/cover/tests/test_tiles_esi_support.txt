ESI support
===========

Marking a tile as ESI-rendered
------------------------------

For ESI rendering to be available, the tile must be marked with the
``IESIRendered`` marker interface, but collective.cover.base is marked, then we can create a dummy tile with this
interface like so:

    >>> from zope.interface import implements
    >>> from plone.tiles.interfaces import IESIRendered
    >>> from collective.cover.tiles.base import IPersistentCoverTile
    >>> from collective.cover.tiles.base import PersistentCoverTile

    >>> class BasicTile(PersistentCoverTile):
    ...     implements(IPersistentCoverTile)
    ...
    ...     __name__ = 'collective.cover.sample' # would normally be set by ZCML handler
    ...
    ...     def __call__(self):
    ...         return "<html><head><title>Title</title></head><body><b>My tile</b></body></html>"

Above, we have created a simple HTML string. This would normally be rendered
using a page template.

We'll register this tile manually here. Ordinarily, of course, it would be
registered via ZCML.

    >>> from plone.tiles.type import TileType
    >>> BasicTileType = TileType(
    ...     name=u'collective.cover.sample',
    ...     title=u"Sample basic tile",
    ...     description=u"A tile used for testing",
    ...     add_permission="dummy.Permission",
    ...     schema=".basic.BasicTile")

    >>> from zope.component import provideAdapter, provideUtility
    >>> from zope.interface import Interface
    >>> from collective.cover.tiles.basic import IBasicTile

    >>> provideUtility(BasicTileType, name=u'collective.cover.sample')
    >>> provideAdapter(BasicTile, (Interface, Interface), IBasicTile, name=u"collective.cover.sample")

ESI lookup
----------

When a page is rendered (for example by a system like ``plone.app.blocks``,
but see below), a tile placeholder may be replaced by a link such as::

    <esi:include src="/path/to/context/@@collective.cover.sample/tile1/@@esi-body" />

When this is resolved, it will return the body part of the tile. Equally,
a tile in the head can be replaced by::

    <esi:include src="/path/to/context/@@collective.cover.sample/tile1/@@esi-head" />

To illustrate how this works, let's create a sample context, look up the view
as it would be during traversal, and instantiate the tile, before looking up
the ESI views and rendering them.

    >>> from zope.interface import implements

    >>> class IContext(Interface):
    ...     pass

    >>> class Context(object):
    ...     implements(IContext)

    >>> from zope.publisher.browser import TestRequest

    >>> class IntegratedTestRequest(TestRequest):
    ...     @property
    ...     def environ(self):
    ...         return self._environ

    >>> context = Context()
    >>> request = IntegratedTestRequest()

    >>> from zope.interface import Interface
    >>> from zope.component import getMultiAdapter

The following simulates traversal to ``context/@@collective.cover.sample/tile1``

    >>> tile = getMultiAdapter((context, request), name=u"collective.cover.sample")
    >>> tile = tile['tile1'] # simulates sub-path traversal

This tile should be ESI rendered::

    >>> IESIRendered.providedBy(tile)
    True

At this point, we can look up the ESI views:

    >>> head = getMultiAdapter((tile, request), name="esi-head")
    >>> print head()
    <title>Title</title>

    >>> body = getMultiAdapter((tile, request), name="esi-body")
    >>> print body()
    <b>My tile</b>

Convenience classes and placeholder rendering
---------------------------------------------

Two convenience base classes can be found in the ``collective.cover.base`` module. These extend the standard ``PersistentCoverTile`` class
to provide the ``IESIRendered`` interface.

Additionally, these base classes implement a ``__call__()`` method that will
render a tile placeholder if the request contains an ``X-ESI-Enabled``
header set to the literal 'true'.

The placeholder is a simple HTML ``<a />`` tag, which can be transformed into
an ``<esi:include />`` tag using the helper function ``substituteESILinks()``.
The reason for this indirection is that the ``esi`` namespace is not allowed
in HTML documents and are liable to be stripped out by transforms using the
``libxml2`` / ``lxml`` HTML parser.

Let us now create a simple basic ESI tile. To benefit from the default rendering,
we should implement the ``render()`` method instead of ``__call__()``. Setting
a page template as the ``index`` class variable or using the ``template``
attribute to the ZCML directive will work also.

    >>> from collective.cover.tiles.base import PersistentCoverTile

    >>> class BasicTile(PersistentCoverTile):
    ...     __name__ = 'collective.cover.sample' # would normally be set by ZCML handler
    ...
    ...     def render(self):
    ...         return "<html><head><title>Title</title></head><body><b>My basic ESI tile</b></body></html>"

    >>> BasicTileType = TileType(
    ...     name=u'collective.cover.sample',
    ...     title=u"Sample basic ESI tile",
    ...     description=u"A tile used for testing ESI",
    ...     add_permission="dummy.Permission",
    ...     schema=".basic.BasicTile")

    >>> provideUtility(BasicTileType, name=u'collective.cover.sample')
    >>> provideAdapter(BasicTile, (Interface, Interface), IBasicTile, name=u"collective.cover.sample")

The following simulates traversal to ``context/@@collective.cover.sample/tile1``

    >>> tile = getMultiAdapter((context, request), name=u"collective.cover.sample")
    >>> tile = tile['tile1'] # simulates sub-path traversal

By default, the tile renders as normal:

    >>> print tile()
    <html><head><title>Title</title></head><body><b>My basic ESI tile</b></body></html>

However, if we opt into ESI rendering via a request header ``X-ESI-Enabled``, we get a different
view:

    >>> from plone.tiles.interfaces import ESI_HEADER_KEY
    >>> request.environ[ESI_HEADER_KEY] = 'true'
    >>> print tile() # doctest: +NORMALIZE_WHITESPACE
    <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
        "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
    <html xmlns="http://www.w3.org/1999/xhtml">
        <body>
            <a class="_esi_placeholder"
               rel="esi"
               href="http://127.0.0.1/@@esi-body?"></a>
        </body>
    </html>

This can be transformed into a proper ESI tag with ``substituteESILinks()``:

    >>> from plone.tiles.esi import substituteESILinks
    >>> print substituteESILinks(tile()) # doctest: +NORMALIZE_WHITESPACE
    <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
        "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
    <html xmlns:esi="http://www.edge-delivery.org/esi/1.0" xmlns="http://www.w3.org/1999/xhtml">
        <body>
            <esi:include src="http://127.0.0.1/@@esi-body?" />
        </body>
    </html>

It is also possible to render the ESI tile for the head. This is done with
a class variable 'head' (which would of course normally be set within the
class):

    >>> BasicTile.head = True
    >>> print tile() # doctest: +NORMALIZE_WHITESPACE
    <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
        "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
    <html xmlns="http://www.w3.org/1999/xhtml">
        <body>
            <a class="_esi_placeholder"
               rel="esi"
               href="http://127.0.0.1/@@esi-head?"></a>
        </body>
    </html>