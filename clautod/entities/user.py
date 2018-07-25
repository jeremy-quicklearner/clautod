"""
User-related entities for Clautod
"""

# IMPORTS ##############################################################################################################

# Standard Python modules
from datetime import datetime
from hashlib import sha256

# Other Python modules

# Clauto Common Python modules
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
        self.password = Validator().validate_password(password, True)

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

class UserDummy:
    """
    A Clauto user - dummy class with no behaviour
    """

    def __init__(self, username=None, password=None, privilege_level=0, password_salt=None, password_hash=None):
        """
        Create a dummy user given some of: a username, password, privilege level, salt, and hash
        :param username: The username
        :param password: The password
        :param privilege_level: The privilege level
        :param password_salt: The salt
        :param password_hash: The hash
        """
        # Initialize fields
        self.username = Validator().validate_username(username, True)
        self.password = Validator().validate_password(password, True)
        self.privilege_level = Validator().validate_privilege_level(privilege_level, True)
        self.password_salt = Validator().validate_int(password_salt, True, 0, None)
        self.password_hash = Validator().validate_string(password_hash, True, False, False)

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
