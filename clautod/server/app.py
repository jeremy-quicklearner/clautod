"""
Entry point for clautod
"""

# IMPORTS ##############################################################################################################

# Standard Python modules
import sys
import traceback

# Other Python modules

# Clauto Common Python modules
from clauto_common.patterns.singleton import Singleton
from clauto_common.util.config import ClautoConfig
from clauto_common.util.log import Log

# Clautod Python modules


# CONSTANTS ############################################################################################################

# CLASSES ##############################################################################################################

class ClautodFlaskApp(Singleton):

    def __init__(self):
        """
        Constructor for ClautodFlaskApp class
        """

        # Singleton Initialization
        Singleton.__init__(self, __class__)
        if Singleton.is_initialized(__class__):
            return

        # Initialize config
        self.config = ClautoConfig()

        # Initialize logging
        self.log = Log("clautod")
        self.log.debug("Flask App initializing...")

        # Initialization complete
        self.log.debug("Flask App initialized")
