#!/usr/bin/env python

from distutils.core import setup

name = 'f3utils'
version = '0.9'

setup(
    name=name,
    version=version,
    description='Utilities from the F3 ERP suite',
    long_description="A handful of generic utilities",
    license='LGPLv3',
    platforms='Platform Independent',
    author="Panos Christeas",
    author_email='xrg@pefnos.com',
    # url='http://git.hellug.gr/?p=xrg/openerp-libcli',
    # download_url="http://git.hellug.gr/?p=xrg/openerp-libcli",
    packages=['f3utils'],
    keywords=['f3', 'python',],
    classifiers=[
          'Development Status :: 4 - Beta',
          'Environment :: Libraries',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: LGPL v3',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Topic :: Software Development :: Libraries :: Python Modules',
          'Topic :: System :: Filesystems',
          ],
    )
