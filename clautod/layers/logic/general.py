"""
General logic layer for Clautod
"""

# IMPORTS ##############################################################################################################

# Standard Python modules

# Other Python modules

# Clauto Common Python modules
from clauto_common.patterns.singleton import Singleton
from clauto_common.util.config import ClautoConfig
from clauto_common.util.log import Log


# Clautod Python modules
from layers.database.general import ClautodDatabaseLayer
from layers.logic.user import ClautodLogicLayerUser


# CONSTANTS ############################################################################################################

# CLASSES ##############################################################################################################

class ClautodLogicLayer(Singleton):
    """
    Clautod logic layer
    """

    def __init__(self):
        """
        Initialize the logic layer
        """

        # Singleton instantiation
        Singleton.__init__(self)
        if Singleton.is_initialized(self):
            return

        # Initialize config
        self.config = ClautoConfig()

        # Initialize logging
        self.log = Log("clautod")
        self.log.debug("Logic layer initializing...")

        # Initialize Database Layer
        self.database_layer = ClautodDatabaseLayer()

        # Initialize facilities
        self.user_facility = ClautodLogicLayerUser()

        # Initialization complete
        self.log.debug("Logic layer initialized")
