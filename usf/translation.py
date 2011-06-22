'''
This module setup translation environment

XXX it's a bit magical and "polute" the importing context, which get a _ method
defined without importing it explicitly.

'''

import os
import gettext
# Set up message catalog access
#t = gettext.translation('ultimate_smash_friends', 'locale', fallback=True)
#_ = t.ugettext

from usf.config import Config

CONFIG = Config()
LOCALE_DIR = os.path.join(CONFIG.sys_data_dir, "po")

#XXX _ is magicaly definied by the next line :/
gettext.install("ultimate-smash-friends", LOCALE_DIR)
_("translator-credits")
