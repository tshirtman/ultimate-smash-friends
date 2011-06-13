import os
import gettext
# Set up message catalog access
#t = gettext.translation('ultimate_smash_friends', 'locale', fallback=True)
#_ = t.ugettext

from usf.config import Config

CONFIG = Config()
LOCALE_DIR = os.path.join(CONFIG.sys_data_dir, "po")
gettext.install("ultimate-smash-friends", LOCALE_DIR)
_("translator-credits")
