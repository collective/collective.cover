# -*- coding: utf-8 -*-
from collective.cover import patches
from zope.i18nmessageid import MessageFactory


_ = MessageFactory("collective.cover")

patches.run()
