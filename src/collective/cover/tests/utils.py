# -*- coding: utf-8 -*-
from plone.app.robotframework.remote import RemoteLibrary

import os

BUILDOUT_DIRECTORY = os.environ['PWD']


class Utils(RemoteLibrary):

    """Robot Framework helper methods used in this package."""
