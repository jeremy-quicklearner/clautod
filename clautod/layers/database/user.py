"""
User facility of database layer for Clautod
"""

# IMPORTS ##############################################################################################################

# Standard Python modules

# Other Python modules

# Clauto Common Python modules
from clauto_common.patterns.singleton import Singleton
from clauto_common.util.config import ClautoConfig
from clauto_common.util.log import Log
from clauto_common.exceptions import MissingSubjectException

# Clautod Python modules
from layers.database.util import ClautoDatabaseConnection
from entities.user import User


# CONSTANTS ############################################################################################################

# CLASSES ##############################################################################################################

class ClautodDatabaseLayerUser(Singleton):
    """
    Clautod database layer user facility
    """

    def __init__(self):
        """
        Initialize the user database layer
        """

        # Singleton instantiation
        Singleton.__init__(self)
        if Singleton.is_initialized(self):
            return

        # Initialize config
        self.config = ClautoConfig()

        # Initialize logging
        self.log = Log("clautod")

        self.log.verbose("Database layer user facility initialized")

    def get_by_username(self, username):
        """
        Gets a user record from the database
        :param username: The username of the user to get
        :return: A User object containing the requested user's data
        """

        self.log.verbose("Selecting user from database by username <%s>", username)
        with ClautoDatabaseConnection() as db:
            user_record = db.get_record_by_key("users", "username", username, 4, False)
        if not user_record:
            self.log.verbose("Username <%s> not present in database", username)
            raise MissingSubjectException

        username, privilege_level, password_salt, password_hash = user_record
        self.log.verbose("Found user <%s> in database", username)
        return User(username, None, privilege_level, password_salt, password_hash)
