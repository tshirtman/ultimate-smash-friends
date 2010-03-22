import os
import gettext
# Set up message catalog access
#t = gettext.translation('ultimate_smash_friends', 'locale', fallback=True)
#_ = t.ugettext

from config import Config

config = Config.getInstance()
locale_dir = os.path.join(config.data_dir, "locale")
gettext.install("messages", locale_dir)

