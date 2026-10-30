"""Bot user-facing texts.

DEPRECATED: all user-facing strings now live in :mod:`bot.i18n`
(``tg_bot/bot/i18n.py``), which holds the English and Russian translations.
This module only re-exports the current-language strings for backward
compatibility — edit ``i18n.py`` instead of this file.
"""
from bot.i18n import t

# Shown on /start (welcome screen with the "Fill in the request" button).
WELCOME = t("welcome")

# Shown after the user presses the "Submit request" button.
SUBMITTED = t("submitted")
