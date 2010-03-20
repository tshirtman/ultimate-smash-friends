#!/usr/bin/env python

""" The files method was adapted from the AutoDataDiscovery solution in the
    official Distutils Cookbook:
    http://wiki.python.org/moin/Distutils/Cookbook/AutoDataDiscovery

"""
import os from sys import exit
import platform
import imp
from distutils.core import setup

OS = platform.system().lower()

def files(path):
    """ Return all non-python-file filenames in path """
    result = []
    all_results = []
    module_suffixes = [info[0] for info in imp.get_suffixes()]
    ignore_dirs = ['cvs']
    for item in os.listdir(path):
        name = os.path.join(path, item)
        if (
            os.path.isfile(name) and
            os.path.splitext(item)[1] not in module_suffixes
            ):
            result.append(name)
        elif os.path.isdir(name) and item.lower() not in ignore_dirs:
            all_results.extend(files(name))
    if result:
        all_results.append([path, result])
    return all_results

if OS == 'windows':
    # TODO: change to sane install locations for windows
    print "Sorry, setup.py is currently unable to build a proper windows" 
          " executable."
    exit(1)
    """
    data = [('Ultimate Smash Friends' + item[0], item[1])
            for item in files('.')]
    """
else:
    data = [('share/ultimate-smash-friends/' + item[0], item[1]) 
            for item in files('data')]

    doc = [('share/doc/ultimate-smash-friends' + 
            item[0].replace('doc', ''), item[1]) 
            for item in files('doc')]
    doc[-1][-1].append('COPYING.txt')
    doc[-1][-1].append('CREDITS')
    doc[-1][-1].append('README.txt')
    doc[-1][-1].append('README.fr.txt')

    etc = [('/etc/ultimate-smash-friends/', 
            ['default_keys.cfg', 'default_sound.cfg', 'default_config.cfg', 
             'system.cfg'])]

setup(name='ultimate-smash-friends',
      version='0.0.5',
      description=('A 2d arcade fight game, based on the gameplay of super '
                   'smash bros, from nintendo.'),
      author='Gabirel Pettier',
      author_email='gabriel.pettier@gmail.com',
      maintainer='Edwin Marshall (aspidites',
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
      scripts=['ultimate-smash-friends', 'utils/viewer', 'utils/togimpmap', 
               'utils/tolevel', 'utils/xml_text_extractor'],
      requires=['pygame (>=1.6)'],
      data_files = [] if OS == 'windows' else data + doc + etc
     )
