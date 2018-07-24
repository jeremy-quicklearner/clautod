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

    def get(self, username=None, privilege_level=None, password_salt=None, password_hash=None):
        """
        Gets user records from the database
        :param username: The username to select by
        :param privilege_level: The privilege level to select by
        :param password_salt: The password salt to select by
        :param password_hash: The password hash to select by
        :return: An array of User objects that matched the selection criteria
        """
        self.log.verbose(
            "Selecting users from database with selection criteria "
            "<username=%s,privilege_level=%s,password_salt=%s,password_hash=%s>",
            username, privilege_level, password_salt, password_hash
        )
        constraints = {}
        if username:        constraints["username"] =        username
        if privilege_level: constraints["privilege_level"] = privilege_level
        if password_salt:   constraints["password_salt"] =   password_salt
        if password_hash:   constraints["password_hash"] =   password_hash
        with ClautoDatabaseConnection() as db:
            user_records = db.get_records_by_simple_constraint_intersection("users", constraints, None, None, 4)
        usernames =        [user_record[0] for user_record in user_records]
        privilege_levels = [user_record[1] for user_record in user_records]
        password_salts =   [user_record[2] for user_record in user_records]
        password_hashes =  [user_record[3] for user_record in user_records]
        return [
            User(username, None, privilege_level, a_password_salt, a_password_hash)
            for (username, privilege_level, a_password_salt, a_password_hash)
            in zip(usernames, privilege_levels, password_salts, password_hashes)
        ]

    def get_by_username(self, username):
        """
        Gets a user record from the database
        :param username: The username of the user to get
        :return: A User object containing the requested user's data
        """

        self.log.verbose("Selecting user from database by username <%s>", username)
        try:
            return self.get(username, None, None, None)[0]
        except IndexError:
            raise MissingSubjectException

    def get_all(self):
        """
        Gets every user record in the database
        :return: An array of user objects for all users in the database
        """

        self.log.verbose("Selecting all users from database")
        return self.get(None, None, None, None)