"""
User facility of logic layer for Clautod
"""

# IMPORTS ##############################################################################################################

# Standard Python modules

# Other Python modules

# Clauto Common Python modules
from clauto_common.patterns.singleton import Singleton
from clauto_common.util.config import ClautoConfig
from clauto_common.util.log import Log
from clauto_common.access_control import PRIVILEGE_LEVEL_PUBLIC
from clauto_common.exceptions import MissingSubjectException
from clauto_common.exceptions import InvalidCredentialsException

# Clautod Python modules
from layers.database.general import ClautodDatabaseLayer
from entities.user import User


# CONSTANTS ############################################################################################################

# CLASSES ##############################################################################################################

class ClautodLogicLayerUser(Singleton):
    """
    Clautod logic layer user facility
    """

    def __init__(self):
        """
        Initialize the user logic layer
        """

        # Singleton instantiation
        Singleton.__init__(self)
        if Singleton.is_initialized(self):
            return

        # Initialize config
        self.config = ClautoConfig()

        # Initialize logging
        self.log = Log("clautod")

        # Initialize database layer
        self.database_layer = ClautodDatabaseLayer()

        self.log.verbose("Logic layer user facility initialized")

    def get(self, filter_user):
        """
        Gets a user from the database
        :param filter_user: A dummy user object with instance variables to filter the database records by
        :return: An array of user objects from the database with instance variables conforming to the filter
        """
        self.log.verbose("Retrieving users from database layer with filter object <%s>", str(filter_user.to_dict()))
        return self.database_layer.user_facility.get(filter_user)

    def authenticate(self, given_user):
        """
        Given a User object containing a username and password,
        authenticate that the user exists in the database and has
        the expected password hash
        :param given_user: A user object with a username and password from a login attempt
        :return: The User from the DB
        """

        # Get the real user from the DB
        self.log.verbose("Finding username <%s> in database", given_user.username)
        try:
            user_from_db = self.database_layer.user_facility.get_by_username(given_user.username)
        except MissingSubjectException:
            self.log.verbose("Username <%s> not present in DB. Authentication failed.", given_user.username)
            raise

        # Recreate the User using the given password, and the salt from the user in the DB
        # This instantiation calculates the password hash in its constructor
        self.log.verbose("Calculating salted hash of login password")
        user_from_login = User(
            username=given_user.username,
            password=given_user.password,
            privilege_level=PRIVILEGE_LEVEL_PUBLIC, # This parameter doesn't matter but it's required by the User class
            password_salt=user_from_db.password_salt
        )

        # Compare the user trying to login with the user from the db
        self.log.verbose("Comparing salted hash of login password against salted hash from DB")
        if user_from_login.password_hash != user_from_db.password_hash:
            self.log.verbose("Credentials given for username <%s> failed validation. Authentication failed.",
                             user_from_login.username)
            raise InvalidCredentialsException

        # Success!
        self.log.verbose("Authenticated user <%s>.", given_user.username)
        return user_from_db
