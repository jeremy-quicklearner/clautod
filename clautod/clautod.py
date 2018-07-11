"""
Entry point for clautod
"""

# IMPORTS ##############################################################################################################

# Standard Python modules

# Other Python modules

# Clauto Common Python modules
from clauto_common.patterns.singleton import Singleton
from clauto_common.util.log import Log
from clauto_common.exceptions import ClautodAlreadyInstantiatedException
from clauto_common.exceptions import exception_to_exit_code
from clauto_common.exceptions import EXIT_ERROR

# Clautod Python modules
from layers.service.general import ClautodServiceLayer
from layers.logic.general import ClautodLogicLayer
from layers.database.general import ClautodDatabaseLayer

# CONSTANTS ############################################################################################################

# CLASSES ##############################################################################################################

class Clautod(Singleton):

    def __init__(self):
        """
        Constructor for Clautod class. Loads the config file, initializes the layers with it, and runs the WSGI server
        """

        Singleton.__init__(self, __class__)
        # If Clautod has already been instantiated in the same process, there's something seriously broken
        if Singleton.is_initialized(__class__):
            self.log.critical("Clautod is already instantiated in the same process. Something is seriously broken.")
            raise ClautodAlreadyInstantiatedException()


        # Load the config
        self.config = {"log_dir": "/var/log/clauto", "log_level_default": "INF"} #TODO: Read the config file with configargparse

        # Initialize the log
        self.log = Log("clautod", self.config["log_dir"])
        self.log.level_set("INF")

        # Log the config
        for setting, value in self.config.items():
            self.log.config("Loaded <%s> = <%s>", setting, value)

        # Initialize the database layer
        self.database_layer = ClautodDatabaseLayer(self.config)

        # Initialize the logic layer
        self.logic_layer = ClautodLogicLayer(self.config)

        # Initialize the service layer
        self.service_layer = ClautodServiceLayer(self.config)

        # Start the WSGI Server
        while(True):
            pass

# HELPERS ##############################################################################################################

# MAIN #################################################################################################################

def main():
    """
    Instantiate the Clautod class. Its constructor will take it from here.
    If an exception makes it this far up without being handled, crash.
    """
    try:
        Clautod()
    except Exception as e:
        #try:
            return exception_to_exit_code[e.__class__]
        #except KeyError:
        #    return exception_to_exit_code["default"]

    return EXIT_ERROR


# ENTRY POINT ##########################################################################################################

if __name__ == "__main__":
    exit(main())