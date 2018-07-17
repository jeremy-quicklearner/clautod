"""
General service layer for Clautod
"""

# IMPORTS ##############################################################################################################

# Standard Python modules

# Other Python modules

# Clauto Common Python modules
from clauto_common.patterns.singleton import Singleton
from clauto_common.util.config import ClautoConfig
from clauto_common.util.log import Log

# Clautod Python modules
from layers.logic.general import ClautodLogicLayer
from layers.database.general import ClautodDatabaseLayer
from layers.service.user import ClautodServiceLayerUser


# CONSTANTS ############################################################################################################

# CLASSES ##############################################################################################################

class ClautodServiceLayer(Singleton):
    """
    Clautod service layer
    """

    def __init__(self):
        """
        Initialize the service layer
        """

        # Singleton instantiation
        Singleton.__init__(self)
        if Singleton.is_initialized(self):
            return

        # Initialize config
        self.config = ClautoConfig()

        # Initialize logging
        self.log = Log("clautod")
        self.log.debug("Service layer initializing...")

        # Initialize Database and Logic Layers
        self.database_layer = ClautodDatabaseLayer()
        self.logic_layer = ClautodLogicLayer()

        # Initialize facilities
        self.user_facility = ClautodServiceLayerUser()

        # Initialization complete
        self.log.debug("Service layer initialized")
