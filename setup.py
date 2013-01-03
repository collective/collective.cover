from setuptools import setup, find_packages
import os

version = '1.0a1'
long_description = open("README.txt").read() + "\n" + \
                   open(os.path.join("docs", "INSTALL.txt")).read() + "\n" + \
                   open(os.path.join("docs", "CREDITS.txt")).read() + "\n" + \
                   open(os.path.join("docs", "HISTORY.txt")).read()

setup(name='collective.cover',
      version=version,
      description="An easy-to-use package to create complex covers for Plone sites.",
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
        'setuptools',
        'Pillow',
        'Plone>=4.2',
        'collective.js.jqueryui',
        'plone.app.blocks',
        'plone.app.dexterity[grok]',
        'plone.app.jquery>=1.7.2',
        'plone.app.jquerytools>=1.5.1',
        'plone.app.lockingbehavior',
        'plone.app.stagingbehavior',
        'plone.app.tiles',
        'plone.namedfile[blobs]',
        'plone.principalsource',
        'plone.tiles>=1.2',
        ],
      extras_require={
        'test': [
          'plone.app.testing',
          'plone.app.imagetile',
          'plone.app.texttile',
          'robotsuite',
          'robotframework-selenium2library',
          ],
        },
      entry_points="""
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
