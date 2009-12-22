#!/usr/bin/env python

# extract label strings from xml files to a dummy .py file
# to be able to use them with gettext

import os
import re
from usf_modules.config import config

PATH = os.sep.join((config['MEDIA_DIRECTORY'], 'gui'))

regex_str = re.compile('value *= *".*?"')

strings = []

for file in os.listdir(PATH):
    if ".usfgui" in file:
        f = open(os.sep.join((PATH, file)))
        s = f.read()
        f.close()
        strings.extend(re.findall(regex_str, s))

f = open('strings.py', 'w')
for s in strings:
    if ".png" not in s:
        f.write(s+'\n')
f.close()
