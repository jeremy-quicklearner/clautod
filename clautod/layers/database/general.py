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
from layers.database.util import ClautoDatabaseConnection
from layers.database.user import ClautodDatabaseLayerUser


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

        # Confirm that the database is available and has the correct version
        with ClautoDatabaseConnection(config) as db:
            user_version_pragma = db.connection.execute("PRAGMA user_version;").fetchall()[0][0]
        with open("/usr/share/clauto/clautod/dbmig/dbversion.txt", "r") as dbversion_file:
            dbversion = int(dbversion_file.read())

        if user_version_pragma != dbversion:
            self.log.error("DB user_version <%s> does not match expected DB version <%s>",
                           user_version_pragma, dbversion)
        else:
            self.log.verbose("DB version is <%s>", user_version_pragma)

        # Initialize each portion of the database layer
        self.user = ClautodDatabaseLayerUser(config)

        # Initialization complete
        self.log.debug("Database layer initialized")
