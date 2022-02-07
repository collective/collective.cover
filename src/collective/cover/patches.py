# -*- coding: utf-8 -*-
from collective.cover.logger import logger
from Products.ZCatalog.query import IndexQuery
from ZPublisher.HTTPRequest import record


def index_query():
    # FIXME: Remove this patch after fixing:
    # https://github.com/plone/Products.CMFPlone/issues/3007
    def patched_init(
        self, request, iid, options=(), operators=("or", "and"), default_operator="or"
    ):
        """Patch original __init__"""
        if iid in request:
            param = request[iid]
            # IndexQuery expects the param to be a dictionary, to extract the
            # 'query' key. See:
            # https://github.com/zopefoundation/Products.ZCatalog/blob/91e7826dcfd196632fb1c9318cd5025b718f1058/src/Products/ZCatalog/query.py#L68
            # However, when we use record notation in the URL, for example:
            # http://localhost:8080/Plone/@@search?end.query:record:list:date=2022-2-2+00%3A00%3A00&end.range:record=min
            # the parameter becomes a record and not a dictionary.
            # If we don't convert from record to dict, the query key is not extracted,
            # causing the error:
            # TypeError: unhashable type: 'record'
            # See:
            # https://github.com/plone/Products.CMFPlone/issues/3007
            if isinstance(param, record):
                request[iid] = dict(param)
        return self.__orig_init__(request, iid, options, operators, default_operator)

    setattr(
        IndexQuery,
        "__orig_init__",
        IndexQuery.__init__,
    )
    setattr(IndexQuery, "__init__", patched_init)

    logger.info("Patched Products.ZCatalog.query.IndexQuery")


def run():
    index_query()
