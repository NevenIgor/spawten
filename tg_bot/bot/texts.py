"""Bot user-facing texts.

All texts now live in ``bot.translations`` (tg_bot/bot/translations.py) so the
bot can be translated into other languages. This module re-exports them as
convenient constants for existing imports.

NOTE: these constants are resolved at import time in the active language
(BOT_LANGUAGE env var, default "ru"). To change wording, edit translations.py.
"""
from bot.translations import t

# Shown on /start (welcome screen with the "Fill in the data" button).
WELCOME = t("welcome")

# Shown on /start when the user already has a submitted request
# (keyboard offers the "View request" button instead of "Fill in the data").
WELCOME_SEEN = t("welcome_seen")

# Shown after the user presses the "Submit request" button.
SUBMITTED = t("submitted")

# Header of the "view request" screen.
VIEW_REQUEST_HEADER = t("view_request_header")

# Shown when there is nothing to display on the "view request" screen.
NO_REQUEST = t("no_request")
