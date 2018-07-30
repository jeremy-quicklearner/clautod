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
from clauto_common.access_control import PRIVILEGE_LEVEL_ADMIN
from clauto_common.exceptions import MissingSubjectException
from clauto_common.exceptions import InvalidCredentialsException
from clauto_common.exceptions import IllegalOperationException

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
        Gets users from the database
        :param filter_user: A user object with instance variables to filter the database records by
        :return: An array of user objects from the database with instance variables conforming to the filter
        """
        self.log.verbose("Getting users from database layer")
        return self.database_layer.user_facility.select(filter_user)

    def set(self, filter_user, update_user):
        """
        Updates  users in the database
        :param filter_user: A dummy object with instance variables to filter the database records to be updated
        :param update_user: A dummy user object with instance variables to update the database records with. Fields
        """

        # Don't log the values because one of them may be a password, salt, or hash
        self.log.verbose("Setting fields in users")

        # See what users the filter will select
        selected_users = self.get(filter_user)

        # Check if the filter will select the admin user. The admin user is a special case
        admin_selected = False
        for current_user in selected_users:
            if current_user.username == "admin":
                admin_selected = True
                break

        # Don't allow the privilege level of admin to change
        if (admin_selected and update_user.privilege_level is not WILDCARD and
                update_user.privilege_level != PRIVILEGE_LEVEL_ADMIN):
            self.log.verbose("Refusing to change privilege level of admin")
            raise IllegalOperationException("Cannot change administrative user's privilege level")

        # Don't allow any user besides admin to have their privilege level set to admin
        if update_user.privilege_level == PRIVILEGE_LEVEL_ADMIN and (
                        len(selected_users) > 1 or (selected_users and not admin_selected)
        ):
            self.log.verbose(
                "Refusing to set privilege level of non-admin user(s) to administrative-or-higher level <%s>",
                update_user.privilege_level
            )
            raise IllegalOperationException("Only the administrative user may have administrative privileges")

        # Usernames aren't allowed to change, so always carry over the filter's username - maybe a wildcard
        update_user.username = filter_user.username

        # If the password is being set, calculate the new salt/hash pair
        # Also, ensure only one user is having their password changed - users should all have different salts,
        # so passwords should all be set at different times.
        if update_user.password is not WILDCARD:
            if len(selected_users) > 1:
                self.log.verbose("Refusing to set password for multiple users at once")
                raise IllegalOperationException("Cannot set password for multiple users at once")

            self.log.verbose("Password change detected. Calculating salted hash.")
            update_user.constrain_hash()

        # Perform the update
        self.database_layer.user_facility.update(filter_user, update_user)

    def add(self, user_new):
        """
        Adds a new user to the database
        :param user_new: The user object to add
        """

        # Don't log all the fields because there must be a password
        self.log.verbose("Adding user <%s>", user_new.username)

        # Make sure the username and privilege level are sanitary
        user_new.verify_username()
        user_new.verify_privilege_level()

        # Make sure the user's salt and hash are set, and their password isn't
        user_new.constrain_hash()

        # Check for username collision
        try:
            self.database_layer.user_facility.select_by_username(user_new.username)
            self.log.verbose(
                "Username collision detected. Refusing to add another user with username <%s>", user_new.username
            )
            raise IllegalOperationException("Username <%s> already exists" % user_new.username)
        except MissingSubjectException:
            pass

        # Perform the insertion
        self.database_layer.user_facility.insert(user_new)

    def delete(self, filter_user):
        """
        Deletes users from the database
        :param filter_user: A user object with instance variables to filter the database records by
        """
        self.log.verbose("Deleting users from database layer")

        # See which users will be deleted
        selected_users = self.get(filter_user)

        # Disallow deleting the admin user
        for current_user in selected_users:
            if current_user.username == "admin":
                self.log.verbose("Refusing to delete the admin user")
                raise IllegalOperationException("The administrative user may not be deleted")

        # Delete the users
        self.database_layer.user_facility.delete(filter_user)

        for user in selected_users:
            self.log.verbose("Deleted user <%s>", user.username)

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
        user_from_login = User(
            username=given_user.username,
            password=given_user.password,
            password_salt=user_from_db.password_salt
        )
        self.log.verbose("Calculating salted hash of login password")
        user_from_login.constrain_hash()

        # Compare the user trying to login with the user from the db
        self.log.verbose("Comparing salted hash of login password against salted hash from DB")
        if user_from_login.password_hash != user_from_db.password_hash:
            self.log.verbose("Credentials given for username <%s> failed validation. Authentication failed.",
                             user_from_login.username)
            raise InvalidCredentialsException

        # Success!
        self.log.verbose("Authenticated user <%s>.", given_user.username)
        return user_from_db
