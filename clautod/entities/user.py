"""
User-related entities for Clautod
"""

# IMPORTS ##############################################################################################################

# Standard Python modules
from datetime import datetime
from hashlib import sha256
from collections import OrderedDict

# Other Python modules

# Clauto Common Python modules
from clauto_common.patterns.wildcard import WILDCARD
from clauto_common.util.validation import Validator
from clauto_common.util.log import Log
from clauto_common.access_control import PRIVILEGE_LEVEL_ADMIN
from clauto_common.exceptions import ConstraintViolation


# Clautod Python modules

# CONSTANTS ############################################################################################################

# CLASSES ##############################################################################################################

class User:
    """
    A Clauto user
    """
    def __init__(
            self,
            username=WILDCARD,
            password=WILDCARD,
            privilege_level=WILDCARD,
            password_salt=WILDCARD,
            password_hash=WILDCARD
    ):
        self.log = Log()
        self.username =        Validator().validate_username(username)
        self.password =        Validator().validate_password(password)
        self.privilege_level = Validator().validate_privilege_level(privilege_level)
        self.password_salt =   Validator().validate_int(password_salt)
        self.password_hash =   Validator().validate_string(password_hash)

    def verify_username(self):
        Validator().verify_not_wildcard(self.username)
        self.log.verbose("Verified username")

    def verify_privilege_level(self):
        Validator().verify_not_wildcard(self.privilege_level)

        # If this is the admin user, it must have admin privilege
        if self.username == "admin":
            if self.privilege_level != PRIVILEGE_LEVEL_ADMIN:
                self.log.verbose("Constraint violation: admin user must have admin privilege")
                raise ConstraintViolation("Non-administrative User cannot have administrative privilege")

        # If this isn't the admin user, it can't have admin privilege
        elif self.privilege_level == PRIVILEGE_LEVEL_ADMIN:
            self.log.verbose("Constraint violation: non-admin user can't have admin privilege")
            raise ConstraintViolation("Non-administrative User cannot have administrative privilege")

        self.log.verbose("Verified privilege level")

    def constrain_privilege_level(self):
        try:
            self.verify_privilege_level()
        except ConstraintViolation:
            self.verify_username()

            # If this is the admin user, it must have admin privilege
            if self.username == "admin":
                self.log.verbose("Constraining privilege level to administrative")
                self.privilege_level = PRIVILEGE_LEVEL_ADMIN

            # If this isn't the admin user, it can't have admin privilege
            elif self.privilege_level == PRIVILEGE_LEVEL_ADMIN:
                self.log.verbose("Constraining privilege level to non-administrative")
                self.privilege_level = PRIVILEGE_LEVEL_ADMIN - 1

            self.log.verbose("Verified privilege level")

    def verify_password(self):
        Validator().verify_not_wildcard(self.password, "password")
        Validator().verify_is_wildcard(self.password_hash, "password_hash")

    def verify_salt(self):
        Validator().verify_not_wildcard(self.password_salt, "password_salt")

    def constrain_salt(self):
        try:
            self.verify_salt()
        except ConstraintViolation:
            self.password_salt = int(datetime.utcnow().timestamp() * (10 ** 6))

    def verify_hash(self):
        Validator().verify_is_wildcard(self.password, "password")
        self.verify_salt()
        Validator().verify_not_wildcard(self.password_hash, "password_hash")

    def constrain_hash(self):
        try:
            self.verify_hash()
        except ConstraintViolation:
            # Make sure there's a password and salt
            self.verify_password()
            self.constrain_salt()

            # Calculate the password hash
            self.password_hash = sha256((self.password + "+" + str(self.password_salt)).encode()).hexdigest()

            # Now that there's a password salt and hash, the password isn't needed
            self.password = WILDCARD

    def to_dict(self):
        """
        Returns a dict representation of the user
        :return: A dict representation of the user
        """
        return {
            "username": self.username,
            "privilege_level": self.privilege_level,
            "password": self.password,
            "password_salt": self.password_salt,
            "password_hash": self.password_hash
        }

    def to_ordered_dict(self):
        """
        Returns an OrderedDict representation of the user
        :return: An OrderedDict representation of the user
        """
        return OrderedDict(self.to_dict().items())
