#!/usr/bin/env python
from __future__ import with_statement

""" The files method was adapted from the AutoDataDiscovery solution in the
    official Distutils Cookbook:
    http://wiki.python.org/moin/Distutils/Cookbook/AutoDataDiscovery

"""

import sys, os, platform, imp
from os import environ, sep
from os.path import abspath, join, splitext, isdir, isfile
from sys import exit
OS = platform.system().lower()

if OS == 'darwin':
    from setuptools import setup
elif OS == 'windows':
    from distutils.core import setup
    import py2exe
else:
    from distutils.core import setup

def files(path):
    """Return all non-python-file filenames in path"""
    result = []
    all_results = []
    module_suffixes = [info[0] for info in imp.get_suffixes()]
    ignore_dirs = ['cvs']
    for item in os.listdir(path):
        name = join(path, item)
        if isfile(name) and splitext(item)[1] not in module_suffixes:
            result.append(name)
        elif isdir(name) and item.lower() not in ignore_dirs:
            all_results.extend(files(name))
    if result:
        all_results.append([path, result])
    return all_results

def isSystemDLL(pathname):
    if os.path.basename(pathname).lower() in ["sdl_ttf.dll", "libogg-0.dll"]:
        return 0
    return origIsSystemDLL(pathname)

if OS == 'windows':
    origIsSystemDLL = py2exe.build_exe.isSystemDLL
    py2exe.build_exe.isSystemDLL = isSystemDLL
    
    DATA = [(item[0], item[1]) for item in files('data')]
    DATA.append('CREDITS.txt')
elif OS == 'darwin':
    DATA = [(item[0], item[1]) for item in files('data')]
    DATA.append('CREDITS.txt')
else:
    DATA = [(join('share', 'ultimate-smash-friends') + sep + item[0], item[1])
            for item in files('data')]
    DATA.append((join('share', 'ultimate-smash-friends') + sep + 'data', ['CREDITS.txt']))

NAME = 'ultimate-smash-friends'
VERSION = '0.1.3'

DOC = [(join('share', 'doc', 'ultimate-smash-friends') +
       item[0].replace('doc', ''), item[1]) for item in files('doc')]
DOC[-1][-1].append('COPYING.txt')
DOC[-1][-1].append('CREDITS.txt')
DOC[-1][-1].append('README.txt')
DOC[-1][-1].append('README.fr.txt')

CONFIG = [(sep + join('etc', 'ultimate-smash-friends'), ['system.cfg'])]

ICON = [(join('share', 'applications'), 
              ['ultimate-smash-friends.desktop'])]

SCRIPTS = ['ultimate-smash-friends',
           'viewer.pyw', 'utils/togimpmap.py', 
           'utils/tolevel.py', 
           'utils/xml_text_extractor.py']

if OS == 'darwin':
    SCRIPTS[0] = 'ultimate-smash-friends.py'

    PLIST = dict(
        CFBundleName=NAME,
        CFBundleShortVersionString=VERSION,
        CFBundleGetInfoString=' '.join([NAME, VERSION]),
        CFBundleExecutable=NAME,
        CFBundleIdentifier='org.pythonmac.ultimate-smash-friends'
    )

    OPTIONS = {'argv_emulation': True}

    setup(name=NAME,
          version=VERSION,
          description=('A 2d arcade fight game, based on the gameplay of super '
                       'smash bros, from nintendo.'),
          author='Gabriel Pettier',
          author_email='gabriel.pettier@gmail.com',
          maintainer='Lucas Baudin (xapantu)',
          maintainer_email='xapantu@gmail.com',
          url='http://usf.tuxfamily.org/',
          classifiers=['Development Status :: 2 - Pre-Alpha',
                       'Operating System :: OS Independent',
                       'Intended Audience :: End Users/Desktop',
                       'License :: OSI Approved :: GNU General Public License (GPL)',
                       'Natural Language :: English',
                       'Programming Language :: Python',
                       'Topic :: Games/Entertainment :: Arcade'
                      ],
          app=[
            dict(script='ultimate-smash-friends.py', plist=PLIST),
          ],
          packages=['usf', 'usf.widgets', 'usf.screen'],
          scripts=SCRIPTS,
          requires=['pygame (>=1.6)', 'python (>=2.5)'],
          data_files=(DATA + DOC + CONFIG + ICON),
          setup_requires=['py2app'],
          options={'py2app': OPTIONS}
         )
else:
    setup(name=NAME,
          version=VERSION,
          description=('A 2d arcade fight game, based on the gameplay of super '
                       'smash bros, from nintendo.'),
          author='Gabriel Pettier',
          author_email='gabriel.pettier@gmail.com',
          maintainer='Lucas Baudin (xapantu)',
          maintainer_email='xapantu@gmail.com',
          url='http://usf.tuxfamily.org/',
          classifiers=['Development Status :: 2 - Pre-Alpha',
                       'Operating System :: OS Independent',
                       'Intended Audience :: End Users/Desktop',
                       'License :: OSI Approved :: GNU General Public License (GPL)',
                       'Natural Language :: English',
                       'Programming Language :: Python',
                       'Topic :: Games/Entertainment :: Arcade'
                      ],
          packages=['usf', 'usf.widgets', 'usf.screen'],
          scripts=SCRIPTS,
          requires=['pygame (>=1.6)', 'python (>=2.5)'],
          data_files=(DATA + DOC + CONFIG + ICON),
	      windows=[{"script" : "ultimate-smash-friends", "icon_resources" : [(1, "data/icon/icon.ico")]}]
         )
