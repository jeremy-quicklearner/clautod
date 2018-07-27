"""
User facility of logic layer for Clautod
"""

# IMPORTS ##############################################################################################################

# Standard Python modules

# Other Python modules

# Clauto Common Python modules
from clauto_common.patterns.singleton import Singleton
from clauto_common.patterns.wildcard import WILDCARD
from clauto_common.util.config import ClautoConfig
from clauto_common.util.log import Log
from clauto_common.access_control import PRIVILEGE_LEVEL_PUBLIC
from clauto_common.access_control import PRIVILEGE_LEVEL_ADMIN
from clauto_common.exceptions import MissingSubjectException
from clauto_common.exceptions import InvalidCredentialsException
from clauto_common.exceptions import IllegalOperationException

# Clautod Python modules
from layers.database.general import ClautodDatabaseLayer
from entities.user import User, UserDummy


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
        return self.database_layer.user_facility.select(filter_user)

    def set(self, filter_user, update_user):
        """
        Updates a user in the database
        :param filter_user: A dummy object with instance variables to filter the database records to be updated
        :param update_user: A dummy user object with instance variables to update the database records with. Fields
        """

        # Don't log the values because one of them may be a password
        self.log.verbose("Setting fields in users matching filter <%s>", str(filter_user.to_dict()))

        # Don't allow the privilege level of admin to change
        if filter_user.matches(UserDummy("admin", WILDCARD, 3, WILDCARD, WILDCARD)) and\
                        update_user.privilege_level is not WILDCARD:
            self.log.verbose("Refusing to change privilege level of admin")
            raise IllegalOperationException("Cannot change administrative user's privilege level")

        # Don't allow any user to have their privilege level set to admin
        if update_user.privilege_level >= PRIVILEGE_LEVEL_ADMIN:
            self.log.verbose("Refusing to set privilege level to administrative-or-higher level <%s>",
                             update_user.privilege_level)
            raise IllegalOperationException("Only the administrative user may have administrative privileges")

        # If the password is being set, use a real User object for the update so that a new salt/hash pair is generated
        if update_user.password:
            update_user = User(
                username=update_user.username,
                password=update_user.password,
                privilege_level=update_user.privilege_level
            )
        else:
            update_user = UserDummy(
                username=update_user.username,
                privilege_level=update_user.privilege_level,
                # The password's gone
                password_salt=update_user.password_salt,
                password_hash=update_user.password_hash
            )

        # Perform the update
        self.database_layer.user_facility.update(filter_user, update_user)

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
            user_from_db = self.database_layer.user_facility.select_by_username(given_user.username)
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
