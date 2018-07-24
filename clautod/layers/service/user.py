"""
User facility of service layer for Clautod
"""

# IMPORTS ##############################################################################################################

# Standard Python modules
import json
from time import time
import traceback
from cryptography.x509 import load_pem_x509_certificate
from cryptography.hazmat.backends import default_backend

# Other Python modules
from werkzeug.exceptions import NotFound
from werkzeug.exceptions import BadRequest
from werkzeug.exceptions import Unauthorized
import jwt

# Clauto Common Python modules
from clauto_common.patterns.singleton import Singleton
from clauto_common.util.config import ClautoConfig
from clauto_common.util.log import Log
from clauto_common.exceptions import NoneException
from clauto_common.exceptions import ValidationException
from clauto_common.exceptions import MissingSubjectException
from clauto_common.exceptions import InvalidCredentialsException

# Clautod Python modules
from layers.logic.general import ClautodLogicLayer
from entities.user import User


# CLASSES ##############################################################################################################

class ClautodServiceLayerUser(Singleton):
    """
    Clautod service layer user facility
    """
    # CONSTRUCTOR ######################################################################################################

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

        # Initialize JWT template (which depends on the config)

        self.jwt_template = {
            "iss": ("Clauto at %s" % self.config["instance_name"]),
            "aud": "Clauto users",
            "iat": None,
            "exp": None,
            "username": None,
            "privilege_level": None
        }

        # Initialize logic layer
        self.logic_layer = ClautodLogicLayer()

        self.log.verbose("Service layer user facility initialized")

    # HELPERS ##########################################################################################################

    def build_jwt_session_token(self, username, privilege_level):
        """
        Builds a JWT session token for the given user
        :param username: The username of the user for which to build the JWT session token
        :param privilege_level: The privilege level of the user for which to build the JWT session token
        :return: The JWT session token
        :return: The claims in the JWT session token
        """

        # Copy the template and fill it in
        jwt_template = self.jwt_template.copy()
        jwt_template["iat"] = int(time())
        jwt_template["exp"] = jwt_template["iat"] + int(self.config["session_lifetime"])
        jwt_template["username"] = username
        jwt_template["privilege_level"] = privilege_level

        # Load the public key
        with open("/etc/clauto/clautod/clauto-pkey.pem", "r") as pemfile:
            pemkey = pemfile.read()
        privkey = bytes("\n".join([l.lstrip() for l in pemkey.split("\n")]), "utf-8")

        # Encode and return the JWT session token
        return jwt.encode(jwt_template, privkey, "RS512").decode("utf-8"), jwt_template

    # EXPOSED ##########################################################################################################

    def renew(self, session_token):
        """
        Given a session token, return a new session token for the same user
        :param session_token: The old session token
        :return: The new session token
        :return: The claims from the new session token
        """

        # If there's no session token, then there's nothing to renew
        if session_token is None or session_token == "None":
            return None, None

        # Load the public key
        with open("/etc/clauto/clautod/clauto-cert.pem", "r") as pemfile:
            pemkey = bytes(pemfile.read(), "utf-8")
        pubkey = load_pem_x509_certificate(pemkey, default_backend()).public_key()

        try:
            claims = jwt.decode(
                session_token,
                pubkey,
                verify=True,
                algorithms=["RS512"],
                issuer=self.jwt_template["iss"],
                audience=self.jwt_template["aud"],
                options={
                    'verify_signature': True,
                    'verify_exp': True,
                    'verify_nbf': False,
                    'verify_iat': True,
                    'verify_aud': True,
                    'verify_username': True,
                    'verify_privilege_level': True,

                    'require_exp': True,
                    'require_iat': True,
                    'require_nbf': False
                }
            )
        except jwt.exceptions.InvalidIssuerError:
            self.log.warning("Session token contains invalid issuer. Possible attack.")
            raise Unauthorized()
        except jwt.exceptions.InvalidAudienceError:
            self.log.warning("Session token contains invalid audience. Possible attack.")
            raise Unauthorized()
        except jwt.exceptions.ExpiredSignatureError:
            self.log.debug("Session token is expired")
            raise Unauthorized("The session is expired")
        except jwt.exceptions.DecodeError:
            for line in (
                "JWT decode failed. Responding to client with HTTP 401. Traceback is below.\n" +
                traceback.format_exc()
            ).split("\n")[:-1]:
                self.log.debug(line)
            raise Unauthorized()

        return self.build_jwt_session_token(claims["username"], claims["privilege_level"])

    # API HANDLERS #####################################################################################################

    def login(self, params):
        """
        Authenticate a login request and respond with a session token
        :param params: Request parameters
            - (Required) username: The username to login with
            - (Required) password: The password to login with
        :return: A JWT session token for the user
        """

        # Construct a User object with the given username and password
        try:
            given_user = User(params.get("username"), params.get("password"))
        except NoneException as e:
            raise BadRequest("Missing parameter: <%s>" % str(e))
        except ValidationException as e:
            raise BadRequest("Invalid parameter value for <%s>" % str(e))

        # Authenticate the user
        try:
            found_user = self.logic_layer.user_facility.authenticate(given_user)
        except MissingSubjectException:
            raise NotFound("User not found")
        except InvalidCredentialsException:
            raise BadRequest("Incorrect Password")

        return self.build_jwt_session_token(found_user.username, found_user.privilege_level)[0]

    def get(self, params):
        """
        Get users from the database
        :param params: Request parameters
            - (Optional) username: Username to filter by
            - (Optional) privilege_level: Privilege level to filter by
        :return: An array of users, in JSON form
        """

        # Extract the filters from params
        # Skip the password_salt and password_hash. Don't expose them to the client
        username = params.get("username")
        privilege_level = params.get("privilege_level")

        # Create the user object to filter by, and fudge the salt
        # and hash because they were initialized by the User constructor
        try:
            user_filter = User(username=username, privilege_level=privilege_level)
        except ValidationException as e:
            raise BadRequest("Validation failed: " + str(e))
        user_filter.password_salt = None
        user_filter.password_hash = None

        # Get the users from the database
        return json.dumps(
            [user.to_dict() for user in self.logic_layer.user_facility.get(user_filter)]
        )

    def patch(self, params):
        raise NotImplemented()  # TODO

    def post(self, params):
        raise NotImplemented()  # TODO

    def delete(self, params):
        raise NotImplemented()  # TODO
