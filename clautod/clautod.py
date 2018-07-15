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
from clauto_common.util.log import Log
from clauto_common.util.config import config_read
from clauto_common.exceptions import ClautodAlreadyInstantiatedException
from clauto_common.exceptions import ConfigKeyException
from clauto_common.exceptions import exception_to_exit_code
from clauto_common.exceptions import EXIT_ERROR

# Clautod Python modules
from server.app import ClautodFlaskApp
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
            # Since Clautod is already initialized, so is the log. So we can log the problem
            self.log.critical("Clautod is already instantiated in the same process. Something is seriously broken.")
            raise ClautodAlreadyInstantiatedException()

        # Load the config
        self.config = config_read("/etc/clauto/clautod/clautod.cfg")

        # Initialize the log
        self.log = Log("clautod", self.config["log_dir"])
        self.log.level_set("INF")
        try:
            self.log.level_set(self.config["log_level_default"])
        except ConfigKeyException:
            self.log.level_set("INF")
            self.log.config("<log_level_default> not found in config. Defaulting to <INF>")

        # From now on, log a stack trace for every exception that makes it this far up
        try:

            # Log the config
            for setting, value in self.config.items():
                self.log.config("Loaded <%s> = <%s>", setting, value)

            # Initialize the database layer
            self.database_layer = ClautodDatabaseLayer()

            # Initialize the logic layer
            self.logic_layer = ClautodLogicLayer()

            # Initialize the service layer
            self.service_layer = ClautodServiceLayer()

            # Start the WSGI Server
            while True:
                pass

        except Exception:
            for line in (
                        "Unhandled exception reached top level. Crashing. Traceback is below.\n" +
                        traceback.format_exc()
            ).split("\n")[:-1]:
                # noinspection PyUnboundLocalVariable
                # I don't know why PyCharm thinks 'self' might not be assigned by this point. It's a parameter.
                self.log.critical(line)
            raise sys.exc_info()[0]


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
        try:
            return exception_to_exit_code[e.__class__]
        except KeyError:
            return exception_to_exit_code["default"]

    # Code should never reach here
    return EXIT_ERROR


# ENTRY POINT ##########################################################################################################

if __name__ == "__main__":
    exit(main())

    # Code should never reach here
    exit(EXIT_ERROR)
