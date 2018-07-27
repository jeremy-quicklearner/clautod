"""
User-related entities for Clautod
"""

# IMPORTS ##############################################################################################################

# Standard Python modules
from datetime import datetime
from hashlib import sha256

# Other Python modules

# Clauto Common Python modules
from clauto_common.patterns.wildcard import WILDCARD
from clauto_common.util.validation import Validator


# Clautod Python modules

# CONSTANTS ############################################################################################################

# CLASSES ##############################################################################################################

class User:
    """
    A Clauto user
    """

    def __init_salt_hash(self, password_salt, password_hash):
        """
        Initialize a user given a salt and hash.
        Intended for manifesting users from the DB
        :param password_salt: The password salt
        :param password_hash: The password hash
        """

        # Initialize the salt and hash
        self.password_salt = password_salt
        self.password_hash = password_hash

        # Don't log the attributes. They're sensitive information

    def __init_password_salt(self, password, password_salt):
        """
        Initialize a user given a password and salt. The hash will be generated.
        Intended for manifesting users from login credentials
        :param password: The password
        :param password_salt: The password salt
        """

        # Validate password
        password = Validator().validate_password(password, True)

        # Hash the password and salt
        password_hash = sha256((str(password) + "+" + password_salt).encode()).hexdigest()

        # Initialize the salt and hash
        self.__init_salt_hash(password_salt, password_hash)

    def __init_password(self, password):
        """
        Initialize a user given a password. The salt and hash will be generated.
        Intended for creating user records
        :param password: The password
        """

        # The password will be validated by __init_password_salt

        # Create the salt
        password_salt = str(int(datetime.utcnow().timestamp() * (10 ** 6)))

        # Initialize the salt and hash
        self.__init_password_salt(password, password_salt)

    def __init__(self, username, password=None, privilege_level=0, password_salt=None, password_hash=None):
        """
        Create a user given a user name and some of: a password, salt, and hash
        :param username: The username
        :param password: The password
        :param privilege_level: The privilege level
        :param password_salt: The salt
        :param password_hash: The hash
        """
        # Initialize username and privilege level
        self.username = Validator().validate_username(username)
        self.privilege_level = Validator().validate_privilege_level(privilege_level)

        if not password_salt:
            self.__init_password(password)
        elif not password:
            self.__init_salt_hash(password_salt, password_hash)
        else:
            self.__init_password_salt(password, password_salt)

    def to_dict(self):
        """
        Returns a dict representation of the user
        :return: A dict representation of the user
        """
        return {
            "username": self.username,
            "privilege_level": self.privilege_level
        }

    def matches(self, user_dummy):
        """
        Returns true if this user can be represented by a given dummy user
        :param user_dummy: The dummy user to check against
        :return: True if this dummy user can be represented by other_user_dummy
        """
        # TODO: Cleanup
        if self.username != user_dummy.username and user_dummy.username is not WILDCARD:
            return False
        if user_dummy.password is not WILDCARD:
            return False
        if self.privilege_level != user_dummy.privilege_level and user_dummy.privilege_level is not WILDCARD:
            return False
        if self.password_salt != user_dummy.password_salt and user_dummy.password_salt is not WILDCARD:
            return False
        if self.password_hash != user_dummy.password_hash and user_dummy.password_hash is not WILDCARD:
            return False

        return True

class UserDummy:
    """
    A Clauto user - dummy class with no behaviour
    """

    def __init__(
            self,
            username=WILDCARD,
            password=WILDCARD,
            privilege_level=WILDCARD,
            password_salt=WILDCARD,
            password_hash=WILDCARD
    ):
        """
        Create a dummy user given some of: a username, password, privilege level, salt, and hash
        :param username: The username
        :param password: The password
        :param privilege_level: The privilege level
        :param password_salt: The salt
        :param password_hash: The hash
        """
        # Initialize fields
        self.username = Validator().validate_username(username, True, True)
        self.password = Validator().validate_password(password, True, True)
        self.privilege_level = Validator().validate_privilege_level(privilege_level, True, True)
        self.password_salt = Validator().validate_int(password_salt, True, True, 0, None)
        self.password_hash = Validator().validate_string(password_hash, True, True, False, False)

    def to_dict(self):
        """
        Returns a dict representation of the user
        :return: A dict representation of the user
        """
        return {
            "username": self.username,
            "password": self.password,
            "privilege_level": self.privilege_level,
            "password_salt": self.password_salt,
            "password_hash": self.password_hash
        }

    def matches(self, other_user_dummy):
        """
        Returns true if this dummy user can be represented by a given dummy user
        :param other_user_dummy: The dummy user to check against
        :return: True if this dummy user can be represented by other_user_dummy
        """
        # TODO: Cleanup
        if self.username != other_user_dummy.username and other_user_dummy.username is not WILDCARD:
            return False
        if self.password != other_user_dummy.password and other_user_dummy.password is not WILDCARD:
            return False
        if self.privilege_level != other_user_dummy.privilege_level and\
                        other_user_dummy.privilege_level is not WILDCARD:
            return False
        if self.password_salt != other_user_dummy.password_salt and other_user_dummy.password_salt is not WILDCARD:
            return False
        if self.password_hash != other_user_dummy.password_hash and other_user_dummy.password_hash is not WILDCARD:
            return False

        return True