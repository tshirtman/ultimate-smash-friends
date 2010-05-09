import os
import gettext
# Set up message catalog access
#t = gettext.translation('ultimate_smash_friends', 'locale', fallback=True)
#_ = t.ugettext

from config import Config

config = Config()
locale_dir = os.path.join(config.sys_data_dir, "locale")
gettext.install("messages", locale_dir)

