import gettext

# Set up message catalog access
t = gettext.translation('ultimate_smash_friends', 'locale', fallback=True)
_ = t.ugettext

