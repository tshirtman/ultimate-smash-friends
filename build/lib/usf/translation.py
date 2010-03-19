import gettext
from usf.config import (
        config
        )
import os
# Set up message catalog access
#t = gettext.translation('ultimate_smash_friends', 'locale', fallback=True)
#_ = t.ugettext
localdir = config['MEDIA_DIRECTORY'] + os.sep + "locale"
gettext.install("messages", localdir)

