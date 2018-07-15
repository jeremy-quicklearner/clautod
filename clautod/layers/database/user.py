"""
User facility of database layer for Clautod
"""

# IMPORTS ##############################################################################################################

# Standard Python modules

# Other Python modules

# Clauto Common Python modules
from clauto_common.patterns.singleton import Singleton
from clauto_common.util.log import Log

# Clautod Python modules
from layers.database.util import ClautoDatabaseConnection
from entities.user import User


# CONSTANTS ############################################################################################################

# CLASSES ##############################################################################################################

class ClautodDatabaseLayerUser(Singleton):
    """
    Clautod database layer
    """

    def __init__(self, config):
        """
        Initialize the user database layer
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

        self.user_get_by_username("admin")

    def user_get_by_username(self, username):
        """
        Gets a user record from the database
        :param username: The username of the user to get
        :return:
        """
        with ClautoDatabaseConnection(self.config) as db:
            user_record = db.get_record_by_key("users", "username", username, 3, False)
        if not user_record:
            return None

        username, password_salt, password_hash = user_record
        return User(username, None, password_salt, password_hash)
