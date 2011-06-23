'''
This module setup translation environment

XXX it's a bit magical and "polute" the importing context, which get a _ method
defined without importing it explicitly.

'''

import os
import gettext
from usf.config import Config

CONFIG = Config()
LOCALE_DIR = os.path.join(CONFIG.sys_data_dir, "po")
# Set up message catalog access

t = gettext.translation('ultimate-smash-friends', LOCALE_DIR, fallback=True)
_ = t.gettext


#XXX _ is magicaly definied by the next line :/
#gettext.install("ultimate-smash-friends", LOCALE_DIR)
_("translator-credits")
