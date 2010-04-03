#!/usr/bin/env python

""" The files method was adapted from the AutoDataDiscovery solution in the
    official Distutils Cookbook:
    http://wiki.python.org/moin/Distutils/Cookbook/AutoDataDiscovery

"""
import os, platform, imp
from os import environ
from os.path import join, splitext, isdir, isfile
from sys import exit
from distutils.core import setup
OS = platform.system().lower()

def files(path):
    """ Return all non-python-file filenames in path """
    result = []
    all_results = []
    module_suffixes = [info[0] for info in imp.get_suffixes()]
    ignore_dirs = ['cvs']
    for item in os.listdir(path):
        name = join(path, item)
        if (
            isfile(name) and
            splitext(item)[1] not in module_suffixes
            ):
            result.append(name)
        elif isdir(name) and item.lower() not in ignore_dirs:
            all_results.extend(files(name))
    if result:
        all_results.append([path, result])
    return all_results

if OS == 'windows':
    data = [(join(environ['PROGRAMFILES'], 'Ultimate Smash Friends\\') + 
             item[0], item[1]) for item in files('data')]
    doc = [(join(environ['PROGRAMFILES'], 'Ultimate Smash Friends\\') +
            item[0], item[1]) for item in files('doc')]
    config = [(join(environ['PROGRAMFILES'], 'Ultimate Smash Friends\\'),
              ['system.cfg'])]
    utils = [(join(environ['PROGRAMFILES'], 'Ultimate Smash Friends\\') +
             item[0], item[1]) for item in files('utils')]

    scripts = [(join(environ['PROGRAMFILES'], 'Ultimate Smash Friends\\'),
               ['ultimate-smash-friends', 'viewer'])]
else:
    data = [(join('share', 'ultimate-smash-friends/') + item[0], item[1])
            for item in files('data')]

    doc = [(join('share', 'doc', 'ultimate-smash-friends') +
           item[0].replace('doc', ''), item[1]) for item in files('doc')]

    config = [(join('/etc', 'ultimate-smash-friends'), ['system.cfg'])]

    icon = [(join('share', 'applications'), 
                  ['ultimate-smash-friends.desktop'])]

doc[-1][-1].append('COPYING.txt')
doc[-1][-1].append('CREDITS')
doc[-1][-1].append('README.txt')
doc[-1][-1].append('README.fr.txt')

setup(name='ultimate-smash-friends',
      version='0.0.8',
      description=('A 2d arcade fight game, based on the gameplay of super '
                   'smash bros, from nintendo.'),
      author='Gabriel Pettier',
      author_email='gabriel.pettier@gmail.com',
      maintainer='Edwin Marshall (aspidites)',
      maintainer_email='aspidites@inbox.com',
      url='http://usf.tuxfamily.org',
      classifiers=['Development Status :: 2 - Pre-Alpha',
                   'Operating System :: OS Independent',
                   'Intended Audience :: End Users/Desktop',
                   'License :: OSI Approved :: GNU General Public License (GPL)',
                   'Natural Language :: English',
                   'Programming Language :: Python',
                   'Topic :: Games/Entertainment :: Arcade'
                  ],
      packages=['usf'],
      scripts=[] if OS == 'windows' else ['ultimate-smash-friends', 'viewer', 
                                          'utils/togimpmap', 'utils/tolevel', 
                                          'utils/xml_text_extractor'],
      requires=['pygame (>=1.6)', 'python (>=2.5)'],
      console=['ultimate-smash-friends'],
      data_files=(data + doc + config + utils + scripts if OS == 'windows' else
                  data + doc + config + icon)
     )
