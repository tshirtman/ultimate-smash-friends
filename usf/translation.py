'''
This module setup translation environment and provide the _ function, which you
should import from it to use.

from usf.translation import _

'''

import os
import gettext



from usf import CONFIG
LOCALE_DIR = os.path.join(CONFIG.system_path, "po")
# Set up message catalog access

_ = gettext.translation(
        'ultimate-smash-friends',
        LOCALE_DIR,
        fallback=True).gettext

