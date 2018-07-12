"""
General database layer for Clautod
"""

# IMPORTS ##############################################################################################################

# Standard Python modules

# Other Python modules

# Clauto Common Python modules
from clauto_common.patterns.singleton import Singleton
from clauto_common.util.log import Log


# Clautod Python modules

# CONSTANTS ############################################################################################################

# CLASSES ##############################################################################################################

class ClautodDatabaseLayer(Singleton):
    """
    Clautod database layer
    """

    def __init__(self, config):
        """
        Initialize the database layer
        :param config:
        """

        # Singleton instantiation
        Singleton.__init__(self, __class__)
        if Singleton.is_initialized(__class__):
            return

        # Initialize config
        self.config = config

        # Initialize logging
        self.log = Log("clautod")
        self.log.debug("Database layer initializing...")

        # Initialization complete
        self.log.debug("Database layer initialized")
