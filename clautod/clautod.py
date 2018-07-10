"""
Entry point for clautod
"""

# IMPORTS ##############################################################################################################

# Standard Python modules

# Other Python modules

# Clauto Common Python modules
from clauto_common.patterns.borg import Borg
from clauto_common.util.log import Log

# CONSTANTS ############################################################################################################

# CLASSES ##############################################################################################################
class ClautodAlreadyInstantiatedException(Exception):
    pass

class Clautod(Borg):

    def __init__(self):
        """
        Constructor for Clautod class. Loads the config file, initializes the layers with it, and runs the WSGI server
        """

        Borg.__init__()

        # If Clautod has already been instantiated in the same process, there's something seriously broken
        if hasattr(self, "config"):
            Log("clautod", self.config.log_dir)\
                .critical("Clautod is already instantiated in the same process. Something is seriously broken.")
            raise ClautodAlreadyInstantiatedException()

        # Read the config

        # Initialize the log

        # Log the config

        # Initialize the database layer

        # Initialize the logic layer

        # Initialize the service layer

        # Start the WSGI Server

# HELPERS ##############################################################################################################

# MAIN #################################################################################################################

if __name__ == "main":
    """
    Instantiate the Clautod class. Its constructor will take it from here.
    """
    Clautod()
