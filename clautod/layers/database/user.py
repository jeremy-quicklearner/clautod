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

# Clautod Python modules
from layers.database.util import ClautoDatabaseConnection
from entities.user import User, UserDummy


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
        Gets user records from the database, filtered by the fields in a dummy user object
        :param user_filter: The dummy user object to filter with
        :return: An array of User objects that matched the selection criteria
        """
        constraints = user_filter.to_dict()
        self.log.verbose("Selecting users matching filter <%s>", str(user_filter.to_dict()))
        if "password" in constraints and constraints["password"] is not WILDCARD: return []

        with ClautoDatabaseConnection() as db:
            user_records = db.get_records_by_simple_constraint_intersection(
                table="users",
                constraints=constraints,
                min_records=None,
                max_records=None,
                num_fields_in_record=4
            )
        usernames =        [user_record[0] for user_record in user_records]
        privilege_levels = [user_record[1] for user_record in user_records]
        password_salts =   [user_record[2] for user_record in user_records]
        password_hashes =  [user_record[3] for user_record in user_records]
        user_objects = [
            User(  username, None, privilege_level,  a_password_salt, a_password_hash)
            for (  username,       privilege_level,  a_password_salt, a_password_hash)
            in zip(usernames,      privilege_levels,   password_salts,  password_hashes)
        ]
        for user in user_objects:
            self.log.verbose("Retrieved user: <%s>", str(user.to_dict()))
        return user_objects


    def update(self, user_filter, user_updates):
        """
        Updates user records in the database, filtered by the fields in a dummy user object
        :param user_filter: The dummy user object to filter with
        :param user_updates: A user object (possibly a dummy) containing fields with which to update the user objects
        """
        # Don't log the fields because the password salt and password hash may be present
        constraints = user_filter.to_dict()
        updates = user_updates.to_dict()
        self.log.verbose("Updating fields in user matching filter <%s>", constraints)

        # The username is the primary key. Omit it from the updates so that it won't change
        del updates["username"]

        # Perform the update
        # Query logging must be disabled as the salt and hash are being updated
        with ClautoDatabaseConnection(False) as db:
            db.update_records_by_simple_constraint_intersection("users", constraints, updates)


    def select_by_username(self, username):
        """
        Gets a user record from the database
        :param username: The username of the user to get
        :return: A User object containing the requested user's data
        """

        self.log.verbose("Selecting user from database by username <%s>", username)
        try:
            return self.select(UserDummy(username, WILDCARD, WILDCARD, WILDCARD))[0]
        except IndexError:
            raise MissingSubjectException

    def select_all(self):
        """
        Gets every user record in the database
        :return: An array of user objects for all users in the database
        """

        self.log.verbose("Selecting all users from database")
        return self.select(UserDummy(WILDCARD, WILDCARD, WILDCARD, WILDCARD))