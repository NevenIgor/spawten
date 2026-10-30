"""Bot user-facing texts.

Edit this file to change welcome / completion messages without touching
handler logic. All texts are kept in English; localization will be added
after deployment.
"""

# Shown on /start (welcome screen with the "Fill in the data" button).
WELCOME = "Test welcome message"

# Shown on /start when the user already has a submitted request
# (keyboard offers the "View request" button instead of "Fill in the data").
WELCOME_SEEN = "You have already submitted a request. You can view it below."

# Shown after the user presses the "Submit request" button.
SUBMITTED = "Test request submission text"

# Header of the "view request" screen.
VIEW_REQUEST_HEADER = "Your request:"

# Shown when there is nothing to display on the "view request" screen.
NO_REQUEST = "No saved request found. Send /start and fill in the form."
