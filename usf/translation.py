import gettext
from usf.config import (
        Config
        )
import os
# Set up message catalog access
#t = gettext.translation('ultimate_smash_friends', 'locale', fallback=True)
#_ = t.ugettext
config = Config.getInstance()
localdir = config.data_dir + os.sep + "locale"
gettext.install("messages", localdir)

