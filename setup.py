# -*- coding:utf-8 -*-

from setuptools import find_packages
from setuptools import setup

version = '1.5b1'
description = 'A sane, working, editor-friendly way of creating front pages and other composite pages. Working now, for mere mortals.'
long_description = (
    open('README.rst').read() + '\n' +
    open('CONTRIBUTORS.rst').read() + '\n' +
    open('CHANGES.rst').read()
)

setup(name='collective.cover',
      version=version,
      description=description,
      long_description=long_description,
      classifiers=[
          'Development Status :: 4 - Beta',
          'Environment :: Web Environment',
          'Framework :: Plone',
          'Framework :: Plone :: 4.2',
          'Framework :: Plone :: 4.3',
          'Intended Audience :: End Users/Desktop',
          'Intended Audience :: System Administrators',
          'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
          'Operating System :: OS Independent',
          'Programming Language :: JavaScript',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2.7',
          'Topic :: Office/Business :: News/Diary',
          'Topic :: Software Development :: Libraries :: Python Modules',
      ],
      keywords='plone cover javascript dexterity',
      author='Carlos de la Guardia et al.',
      author_email='cguardia@yahoo.com',
      url='https://github.com/collective/collective.cover',
      license='GPLv2',
      packages=find_packages('src'),
      package_dir={'': 'src'},
      namespace_packages=['collective'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'AccessControl',
          'Acquisition',
          'collective.js.bootstrap',
          'collective.js.galleria',
          'collective.js.jqueryui',
          'collective.z3cform.datetimewidget',
          'Missing',
          'plone.api >=1.4.11',
          'plone.app.blocks >=2.2.1',
          'plone.app.dexterity [relations]',
          'plone.app.iterate',
          'plone.app.jquery >=1.7.2',
          'plone.app.jquerytools >=1.5.1',
          'plone.app.layout',
          'plone.app.linkintegrity',
          'plone.app.lockingbehavior',
          'plone.app.registry',
          'plone.app.relationfield',
          'plone.app.textfield',
          'plone.app.tiles >=1.1.0',
          'plone.app.uuid',
          'plone.app.vocabularies',
          'plone.autoform',
          'plone.behavior',
          'plone.dexterity',
          'plone.i18n',
          'plone.indexer',
          'plone.memoize',
          'plone.namedfile [blobs]',
          'plone.registry',
          'plone.scale',
          'plone.supermodel',
          'plone.tiles',
          'plone.uuid',
          'plone.z3cform',
          'Products.CMFCore',
          'Products.CMFPlone >=4.2',
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
              'mock',
              'plone.app.robotframework',
              'plone.app.testing [robot] >=4.2.2',
              'plone.browserlayer',
              'plone.cachepurging',
              'plone.testing',
              'Products.PloneFormGen <1.8.0.alpha1',
              'tzlocal',
          ],
      },
      entry_points="""
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
