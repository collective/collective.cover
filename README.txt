================================
Plone 4 buildout for developers
================================

.. contents ::

Introduction
------------

`Buildout <http://www.buildout.org>`_ is a tool which automatically downloads, installs and configures Python software.
Plone developers prefer uses buildout based installation method - it makes it easy to work with source code and developing your own Plone add-ons.

For production site installations please use `standard Plone installer <http://plone.org/download>`_.

Prerequisitements
-----------------

What you need in order to use developer buildout with Plone 4

* Experience using command line tools

* Experience using a text editor to work with configuration files (``buildout.cfg``)

* GCC compiler suite to build native Python extensions (Zope contains C code for optimized parts)

* Python 2.6 (other versions are *not* ok for Plone 4)

* Python Imaging Library installed for your Python interpreter (more below)

* Python `Distribute <http://pypi.python.org/pypi/distribute>`_ installation tool, provided by your operating system
  or installed by hand

Read below from operating system specific instructions how to install these dependencies.

Features
--------

This buildout provides

* Zope start up scripts (one instance)

* ``paster`` command for creating Plone add-ons (different from system-wide installation)

* `test <http://plone.org/documentation/manual/plone-community-developer-documentation/testing-and-debugging/unit-testing>`_ command for running automatic test suites 

* `i18ndude <http://pypi.python.org/pypi/i18ndude>`_  for managing text string translations in Python source code 

* `omelette <http://pypi.python.org/pypi/collective.recipe.omelette>`_ buildout recipe which makes Python egg source code more browseable by using symlinks

* `mr.developer <http://pypi.python.org/pypi/mr.developer>`_ command for managing source code checkouts and updates with buildout repeatable manner

* `collective.developermanual <http://plone.org/documentation/manual/plone-community-developer-documentation>`_ - community managed developer manual for Plone
  in source code form, ready for contributions

Creating Plone 4 buildout installation
------------------------------------------

Install ZopeSkel template package for your system-wide Python using Distribute::

 easy_install ZopeSkel
 
... or upgrade existing installation::

 easy_install -U ZopeSkel

You probably got here by running something like (replace *myplonefoldername* with the target folder where you want to Plone to be installed)::

 zopeskel plone4_buildout myplonefoldername

Now, you need to run (please see remarks regarding your operating system below)::

 python bootstrap.py

This will create ``bin`` folder and ``bin/buildout`` script. If you any time want to change Python interpreter
associated with buildout, or you need to update ``buildout`` script itself to newer version please rerun ``bootsrap.py``.

Now you can run buildout script which will download all Python packages
(.egg files) and create ``parts/`` and ``var/`` folder structure ::

  bin/buildout

If this succesfully completes you can start buildout in foreground mode (Press *CTRL+C* to terminate)::

  bin/instance fg 

Now you can login to your site

  http://localhost:8080

The default user is ``admin`` with password ``admin``. 
After initial start-up admin password is stored in Data.fs databse file and value in ``buildout.cfg`` is ignored.
Please follow `these instructions to change admin password <http://manage.plone.org/documentation/kb/changing-the-admin-password>`_.

Next steps
----------

Creating your first add-on
==========================

Plone 4 buildout comes with ``bin/paster`` command for creating Plone add-ons.

.. note ::

	When working with Plone add-ons, use paster command from buildout bin folder, not the system wide paster command.

Create theme (applies for Plone 4 also)::
	
	bin/zopeskel plone3_theme plonetheme.mythemeid
	
Create Archetypes based content types package::

	bin/zopeskel archetype mycompanyid.content

Create other Plone customizations::

	bin/zopeskel plone mycompanyid.mypackageid

More info

* `Instructions how to use Paster command to create your own add-ons <http://collective-docs.plone.org/tutorials/paste.html>`_ 

Managing source code checkouts with buildout
=============================================

`mr.developer buildout extension <http://pypi.python.org/pypi/mr.developer>`_ command which can be used with buildout to manage your source code repositories
*mr.developer* makes source code checkout from multiple repositores a repeatable task.

Operating system specific instructions 
-------------------------------------------

Ubuntu/Debian
==============

Tested for Ubuntu 10.10.

Install prerequisitements::

	sudo apt-get install python2.6 python-imaging wget build-essential python2.6-dev python-setuptools
	easy_install ZopeSkel

OSX
====

Install `OSX development tools (XCode) <http://developer.apple.com/>`_ from Apple.

Install `Macports <http://www.macports.org/>`_.

Then the following installs dependencies::

	sudo port install python26 py26-pil py26-distribute wget 
	easy_install ZopeSkel

When you run ``bootstrap.py``use the following command to make sure you are using Python interpreter from Macports::

	python2.6 bootstrap.py

Windows
========

Microsoft Windows systems is problematic because
it does not provide to Microsoft Visual C compiler (commercial) which is
required to build native Python extensions.

Please read

* http://plone.org/documentation/kb/using-buildout-on-windows

Other
-----

The orignal copy of these instructions is available at

* https://svn.plone.org/svn/collective/ZopeSkel/trunk/zopeskel/templates/plone4_buildout/README.txt
