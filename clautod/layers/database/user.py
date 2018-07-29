"""
User facility of database layer for Clautod
"""

# IMPORTS ##############################################################################################################

# Standard Python modules

# Other Python modules

# Clauto Common Python modules
from clauto_common.patterns.singleton import Singleton
from clauto_common.patterns.wildcard import WILDCARD
from clauto_common.util.config import ClautoConfig
from clauto_common.util.log import Log
from clauto_common.exceptions import MissingSubjectException
from clauto_common.exceptions import IllegalOperationException
from clauto_common.exceptions import DatabaseStateException
from clauto_common.exceptions import ConstraintViolation

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

    def select(self, user_filter):
        """
        Gets user records from the database, filtered by the fields in a user object
        :param user_filter: The user object to filter with
        :return: An array of User objects that matched the selection criteria
        """
        conditions = user_filter.to_ordered_dict()
        # Don't log the conditions because they may contain a password salt or hash
        if conditions["password"] is not WILDCARD:
            self.log.verbose("Refusing to select users by password")
            raise IllegalOperationException("Cannot select users by password")

        with ClautoDatabaseConnection() as db:
            user_records = db.select_records_by_simple_condition_intersection(
                table="users",
                conditions=conditions,
                min_records=None,
                max_records=None,
                num_fields_in_record=4
            )
        usernames =        [user_record[0] for user_record in user_records]
        privilege_levels = [user_record[1] for user_record in user_records]
        password_salts =   [user_record[2] for user_record in user_records]
        password_hashes =  [user_record[3] for user_record in user_records]
        user_objects = [
            User(username, WILDCARD, privilege_level,  a_password_salt, a_password_hash)
            for (username,           privilege_level,  a_password_salt, a_password_hash)
            in zip(usernames,        privilege_levels,   password_salts,  password_hashes)
        ]
        for user in user_objects:
            # Ensure each user has a username, privilege level, salt, and hash
            try:
                user.verify_username()
                user.verify_privilege_level()
                user.verify_salt_hash()
            except ConstraintViolation as e:
                raise DatabaseStateException(str(e))
            self.log.verbose("Retrieved and verified user <%s>", user.username)
        return user_objects

    # noinspection PyMethodMayBeStatic
    def update(self, user_filter, user_updates):
        """
        Updates user records in the database, filtered by the fields in a user object
        :param user_filter: The dummy user object to filter with
        :param user_updates: A user object (possibly a dummy) containing fields with which to update the user objects
        """
        # Don't log the conditions or updates because the password salt and password hash may be present
        conditions = user_filter.to_ordered_dict()
        updates = user_updates.to_ordered_dict()

        # Don't try to filter by password
        if conditions["password"] is not WILDCARD:
            self.log.verbose("Refusing to update users by password")
            raise IllegalOperationException("Cannot update users by password")

        # Perform the update
        # Query logging must be disabled as the salt and hash may be in the updates
        with ClautoDatabaseConnection(False) as db:
            db.update_records_by_simple_condition_intersection("users", conditions, updates)

    def delete(self, user_filter):
        """
        Deletes user records from the database, filtered by the fields in a user object
        :param user_filter: The dummy user object to filter with
        """
        conditions = user_filter.to_ordered_dict()
        # Don't log the conditions because they may contain a password salt or hash
        if "password" in conditions and conditions["password"] is not WILDCARD:
            self.log.verbose("Refusing to delete users by password")
            raise IllegalOperationException("Cannot delete users by password")

        with ClautoDatabaseConnection() as db:
            db.delete_records_by_simple_condition_intersection(
                table="users",
                conditions=conditions,
            )

        self.log.verbose("Deleted user(s)")

    def select_by_username(self, username):
        """
        Gets a user record from the database
        :param username: The username of the user to get
        :return: A User object containing the requested user's data
        """

        self.log.verbose("Selecting user from database by username <%s>", username)
        try:
            return self.select(User(username))[0]
        except IndexError:
            raise MissingSubjectException

    def select_all(self):
        """
        Gets every user record in the database
        :return: An array of user objects for all users in the database
        """

        self.log.verbose("Selecting all users from database")
        return self.select(User())
