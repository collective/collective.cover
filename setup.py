# -*- coding:utf-8 -*-

from setuptools import find_packages
from setuptools import setup

import os

version = '1.0a4.dev0'
long_description = (
    open("README.rst").read() + "\n" +
    open(os.path.join("docs", "INSTALL.rst")).read() + "\n" +
    open(os.path.join("docs", "CREDITS.rst")).read() + "\n" +
    open(os.path.join("docs", "HISTORY.rst")).read()
)

setup(name='collective.cover',
      version=version,
      description='''An easy-to-use package to create elaborate
                     covers for Plone sites.''',
      long_description=long_description,
      classifiers=[
          "Development Status :: 3 - Alpha",
          "Environment :: Web Environment",
          "Framework :: Plone",
          "Framework :: Plone :: 4.2",
          "Framework :: Plone :: 4.3",
          "Intended Audience :: End Users/Desktop",
          "Intended Audience :: System Administrators",
          "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
          "Operating System :: OS Independent",
          "Programming Language :: JavaScript",
          "Programming Language :: Python",
          "Programming Language :: Python :: 2.6",
          "Programming Language :: Python :: 2.7",
          "Topic :: Office/Business :: News/Diary",
          "Topic :: Software Development :: Libraries :: Python Modules",
      ],
      keywords='plone cover javascript dexterity',
      author='Carlos de la Guardia',
      author_email='cguardia@yahoo.com',
      url='https://github.com/collective/collective.cover',
      license='GPLv2',
      packages=find_packages('src'),
      package_dir={'': 'src'},
      namespace_packages=['collective'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'collective.js.galleria',
          'collective.js.jqueryui',
          'five.grok',
          'Pillow',
          'plone.app.blocks',
          'plone.app.dexterity[grok,relations]',
          'plone.app.jquery>=1.7.2',
          'plone.app.jquerytools>=1.5.1',
          'plone.app.lockingbehavior',
          'plone.app.registry',
          'plone.app.stagingbehavior',
          'plone.app.textfield',
          'plone.app.tiles',
          'plone.batching',
          'plone.dexterity',
          'plone.directives.form',
          'plone.memoize',
          'plone.namedfile[blobs]',
          'plone.registry',
          'plone.tiles>=1.2',
          'plone.uuid',
          'Products.CMFCore',
          'Products.CMFPlone>=4.2',
          'Products.GenericSetup',
          'setuptools',
          'z3c.caching',
          'z3c.form',
          'zope.browserpage',
          'zope.component',
          'zope.event',
          'zope.i18nmessageid',
          'zope.interface',
          'zope.schema',
      ],
      extras_require={
          'test': [
              'plone.app.imagetile',
              'plone.app.testing',
              'plone.app.texttile',
              'plone.browserlayer',
              'plone.cachepurging',
              'plone.testing',
              'Products.PloneFormGen',
              'robotframework-selenium2library',
              'robotsuite',
          ],
      },
      entry_points="""
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
