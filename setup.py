#!/usr/bin/env python

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


NAME = 'ultimate-smash-friends'
VERSION = '0.1.3'
DESCRIPTION = ('A 2d arcade fight game, based on the gameplay of super '
                'smash bros, from nintendo.')
AUTHOR = 'Gabriel Pettier'
AUTHOR_EMAIL = 'gabriel.pettier@gmail.com'
MAINTAINER = 'Lucas Baudin (xapantu)'
MAINTAINER_EMAIL = 'xapantu@gmail.com'
URL = 'http://usf.tuxfamily.org/'
CLASSIFIERS = ['Development Status :: 2 - Pre-Alpha',
               'Operating System :: OS Independent',
               'Intended Audience :: End Users/Desktop',
               'License :: OSI Approved :: GNU General Public License (GPL)',
               'Natural Language :: English',
               'Programming Language :: Python',
               'Topic :: Games/Entertainment :: Arcade'
              ]
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
           'utils/xml_text_extractor.py'
          ]
PACKAGES = ['usf', 'usf.widgets', 'usf.screen', 'usf.subpixel']
REQUIRES = ['pygame (>=1.6)', 'python (>=2.5)']

if OS == 'windows':
    origIsSystemDLL = py2exe.build_exe.isSystemDLL
    py2exe.build_exe.isSystemDLL = isSystemDLL
    DATA = [(item[0], item[1]) for item in files('data')]
    DATA.append('CREDITS.txt')
    WINDOWS=[{"script" : "ultimate-smash-friends", "icon_resources" : [(1, "data/icon/icon.ico")]}]

elif OS == 'darwin':
    DATA = [(item[0], item[1]) for item in files('data')]
    DATA.append('CREDITS.txt')
    SCRIPTS[0] = 'ultimate-smash-friends.py'

    PLIST = dict(CFBundleName=NAME,
                 CFBundleShortVersionString=VERSION,
                 CFBundleGetInfoString=' '.join([NAME, VERSION]),
                 CFBundleExecutable=NAME,
                 CFBundleIdentifier='org.pythonmac.ultimate-smash-friends'
                )
    app=[dict(script='ultimate-smash-friends.py', plist=PLIST)]
    OPTIONS = {'argv_emulation': True}
    WINDOWS = None
else:
    DATA = [(join('share', 'ultimate-smash-friends') + sep + item[0], item[1])
            for item in files('data')]
    DATA.append((join('share', 'ultimate-smash-friends') + sep + 'data', ['CREDITS.txt']))
    WINDOWS = None

setup(name=NAME, version=VERSION, description=DESCRIPTION, 
      author=AUTHOR, author_email=AUTHOR_EMAIL, 
      maintainer=MAINTAINER, maintainer_email=MAINTAINER_EMAIL, url=URL,
      classsifiers=CLASSIFIERS, packages=PACKAGES, scripts=SCRIPTS, 
      requires=REQUIRES, data_files=DATA, windows=WINDOWS)
