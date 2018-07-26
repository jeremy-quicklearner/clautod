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

    def get(self, user_dummy):
        """
        Gets user records from the database, filtered by the fields in a dummy user object
        :param user_dummy: The dummy user object to filter with
        :return: An array of User objects that matched the selection criteria
        """
        self.log.verbose(
            "Selecting users from database with selection criteria "
            "<username=%s,privilege_level=%s,password_salt=%s,password_hash=%s>",
            user_dummy.username, user_dummy.privilege_level, user_dummy.password_salt, user_dummy.password_hash
        )
        constraints=user_dummy.to_dict()
        if "password" in constraints and constraints["password"]: return []
        constraints = {key:constraints[key] for key in constraints.keys() if constraints[key]}

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

    def get_by_username(self, username):
        """
        Gets a user record from the database
        :param username: The username of the user to get
        :return: A User object containing the requested user's data
        """

        self.log.verbose("Selecting user from database by username <%s>", username)
        try:
            return self.get(UserDummy(username, None, None, None))[0]
        except IndexError:
            raise MissingSubjectException

    def get_all(self):
        """
        Gets every user record in the database
        :return: An array of user objects for all users in the database
        """

        self.log.verbose("Selecting all users from database")
        return self.get(UserDummy(None, None, None, None))