__version__ = "0.1.1"

import logging

# Sets up logging messages to be destroyed on default
# Users can configure logging in their own scripts to see messages from this package
logging.getLogger(__name__).addHandler(logging.NullHandler())