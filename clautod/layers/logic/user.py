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

    def get(self, given_user):
        # TODO
        pass

    def authenticate(self, given_user):
        """
        Given a User object containing a username and password,
        authenticate that the user exists in the database and has
        the expected password hash
        :param given_user: A user object with a username and password from a login attempt
        :return: The User from the DB
        """

        # Get the real user from the DB
        try:
            self.log.verbose("Finding username <%s> in database", given_user.username)
            user_from_db = self.database_layer.user_facility.get_by_username(given_user.username)
        except MissingSubjectException:
            self.log.verbose("Username <%s> not present in DB. Denying login.", given_user.username)
            raise

        # Recreate the User using the given password, and the salt from the user in the DB
        self.log.verbose("Calculating hash of password given by (supposedly) user <%s>", given_user.username)
        user_from_login = User(
            given_user.username,
            given_user.password,
            PRIVILEGE_LEVEL_PUBLIC,
            user_from_db.password_salt
        )

        # Compare the user trying to login with the user from the db
        if user_from_login.password_hash != user_from_db.password_hash:
            self.log.verbose("Credentials given for username <%s> failed validation. Denying login.",
                             user_from_login.username)
            raise InvalidCredentialsException

        # Build a JWT session token for the user
        self.log.verbose("Authenticated user <%s>.", given_user.username)

        # Success!
        return user_from_db
