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
from clauto_common.patterns.wildcard import WILDCARD
from clauto_common.util.config import ClautoConfig
from clauto_common.util.log import Log
from clauto_common.util.validation import Validator
from clauto_common.exceptions import NoneException
from clauto_common.exceptions import ValidationException
from clauto_common.exceptions import MissingSubjectException
from clauto_common.exceptions import InvalidCredentialsException
from clauto_common.exceptions import IllegalOperationException

# Clautod Python modules
from layers.logic.general import ClautodLogicLayer
from entities.user import User, UserDummy


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
            self.log.debug("Session token from user <%s> is expired", claims["username"])
            raise Unauthorized("The session is expired")
        except jwt.exceptions.DecodeError:
            for line in (
                "JWT decode failed. Responding to client with HTTP 401. Traceback is below.\n" +
                traceback.format_exc()
            ).split("\n")[:-1]:
                self.log.debug(line)
            raise Unauthorized()

        self.log.verbose("Renewing session for user <%s>", claims["username"])
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
        self.log.verbose("Login request")
        try:
            params = Validator().validate_params(
                params,
                required_param_names=["username", "password"],
                optional_param_names=[]
            )
        except ValidationException as e:
            self.log.debug("Denying login request with invalid parameters: <%s>", str(e))
            raise BadRequest(str(e))
        self.log.verbose("Params: <{'username':'%s','password':********}>", params.get("username"))

        # Construct a dummy User object with the given username and password
        try:
            given_user = UserDummy(
                username=params.get("username"),
                password=params.get("password")
            )
        except ValidationException as e:
            self.log.debug("Invalid parameter in login request: <%s>", str(e))
            raise BadRequest("Invalid parameter value for <%s>" % str(e))

        # Authenticate the user
        self.log.verbose("Authenticating login request from <%s>", given_user.username)
        try:
            found_user = self.logic_layer.user_facility.authenticate(given_user)
        except NoneException as e:
            self.log.debug("Login request with null <%s> denied", str(e))
            raise BadRequest("<%s> cannot be null" % str(e))
        except ValidationException as e:
            self.log.debug("Login request with invalid <%s> denied", str(e))
            raise BadRequest("Invalid <%s>" % str(e))
        except MissingSubjectException:
            self.log.debug("Login denied to user <%s> not present in DB", given_user.username)
            raise NotFound("User not found")
        except InvalidCredentialsException:
            self.log.debug("Login denied to user <%s> due to incorrect password", given_user.username)
            raise BadRequest("Incorrect Password")

        self.log.debug("Accepted login request from user <%s>", given_user.username)
        return self.build_jwt_session_token(found_user.username, found_user.privilege_level)[0]

    def get(self, params):
        """
        Get users from the database
        :param params: Request parameters
            - (Optional) username: Username to filter by
            - (Optional) privilege_level: Privilege level to filter by
        :return: An array of users, in JSON form
        """
        self.log.verbose("GET /user request")
        try:
            params = Validator().validate_params(
                params,
                required_param_names=[],
                optional_param_names=["username", "privilege_level"]
            )
        except ValidationException as e:
            self.log.debug("Denying GET /user request with invalid parameters: <%s>", str(e))
            raise BadRequest(str(e))
        self.log.verbose("Params: <%s>", str(params))

        # Create the dummy User object to filter by
        try:
            user_filter = UserDummy(username=params["username"], privilege_level=params["privilege_level"])
        except ValidationException as e:
            self.log.debug("Invalid parameter in GET /user request: <%s>", str(e))
            raise BadRequest("Validation failed: " + str(e))

        # Get the users from the database
        users_arr = [user.to_dict() for user in self.logic_layer.user_facility.get(user_filter)]
        self.log.debug("GET /user request yields users: <%s>", str(users_arr))
        return json.dumps(users_arr)

    def patch(self, params):
        """
        Edit users in the database
        :param params: Request parameters
            - (Optional) username: Username to filter by
            - (Optional) privilege_level: Privilege level to filter by
            - (Optional) new_privilege_level: Privilege level to be applied to the users
        """
        self.log.verbose("PATCH /user request")
        try:
            params = Validator().validate_params(
                params,
                required_param_names=[],
                optional_param_names=["username", "privilege_level", "new_privilege_level", "new_password"]
            )
        except ValidationException as e:
            self.log.debug("Denying PATCH /user request with invalid parameters: <%s>", str(e))
            raise BadRequest(str(e))
        self.log.verbose("Params: <%s>", str(params))

        # Set the users in the database
        try:
            filter_user = UserDummy(
                username=params["username"],
                privilege_level=params["privilege_level"]
            )
            update_user = UserDummy(
                privilege_level=params["new_privilege_level"],
                password=params["new_password"]
            )
            self.logic_layer.user_facility.set(
                filter_user=filter_user,
                update_user=update_user
            )
        except ValidationException as e:
            self.log.debug("Invalid parameter in PATCH /user request: <%s>", str(e))
            raise BadRequest("Validation failed: " + str(e))
        except IllegalOperationException as e:
            self.log.debug("Refusing illegal PATH /use request: <%s>", str(e))
            raise BadRequest("Illegal operation: <%s>", str(e))

        update_dict = update_user.to_dict()
        if update_dict["password"] is not WILDCARD: update_dict["password"] = "********"
        self.log.info("Set fields of users matching <%s> to <%s>",
                      str(filter_user.to_dict()),
                      str(update_user.to_dict())
                      )
        return json.dumps("Success")


    def post(self, params):
        raise NotImplemented()  # TODO

    def delete(self, params):
        raise NotImplemented()  # TODO
