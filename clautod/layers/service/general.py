"""
General service layer for Clautod
"""

# IMPORTS ##############################################################################################################

# Standard Python modules
import traceback
from time import sleep

# Other Python modules
from werkzeug.exceptions import BadRequest
from werkzeug.exceptions import NotFound
from werkzeug.exceptions import MethodNotAllowed
from werkzeug.exceptions import Unauthorized
from werkzeug.exceptions import Forbidden
from werkzeug.exceptions import NotImplemented
from werkzeug.exceptions import InternalServerError
from flask import Response

# Clauto Common Python modules
from clauto_common.patterns.singleton import Singleton
from clauto_common.util.config import ClautoConfig
from clauto_common.util.log import Log
from clauto_common.access_control import PRIVILEGE_LEVEL_ADMIN
from clauto_common.access_control import PRIVILEGE_LEVEL_WRITE
from clauto_common.access_control import PRIVILEGE_LEVEL_READ
from clauto_common.access_control import PRIVILEGE_LEVEL_PUBLIC

# Clautod Python modules
from layers.logic.general import ClautodLogicLayer
from layers.database.general import ClautodDatabaseLayer
from layers.service.user import ClautodServiceLayerUser


# CONSTANTS ############################################################################################################

# CLASSES ##############################################################################################################

# noinspection PyUnusedLocal
class ClautodServiceLayer(Singleton):
    """
    Clautod service layer
    """

    def __init__(self):
        """
        Initialize the service layer
        """

        # Singleton instantiation
        Singleton.__init__(self)
        if Singleton.is_initialized(self):
            return

        # Initialize config
        self.config = ClautoConfig()

        # Initialize logging
        self.log = Log("clautod")
        self.log.debug("Service layer initializing...")

        # Initialize Database and Logic Layers
        self.database_layer = ClautodDatabaseLayer()
        self.logic_layer = ClautodLogicLayer()

        # Initialize facilities
        self.user_facility = ClautodServiceLayerUser()

        # This dict maps URL paths to their intended HTTP methods, facilities, and handler functions in the service
        # layer
        self.url_path_to_path_info = {
            "/api/ping_public": {
                "GET": {"handler": self.ping, "privilege": PRIVILEGE_LEVEL_PUBLIC}
            },
            "/api/ping_read": {
                "GET": {"handler": self.ping, "privilege": PRIVILEGE_LEVEL_READ}
            },
            "/api/ping_write": {
                "GET": {"handler": self.ping, "privilege": PRIVILEGE_LEVEL_WRITE}
            },
            "/api/ping_admin": {
                "GET": {"handler": self.ping, "privilege": PRIVILEGE_LEVEL_ADMIN}
            },
            "/api/ping_slow": {
                "GET": {"handler": self.ping_slow, "privilege": PRIVILEGE_LEVEL_PUBLIC}
            },
            "/api/user/login": {
                "POST": {"handler": self.user_facility.login, "privilege": PRIVILEGE_LEVEL_PUBLIC}
            },
            "/api/user": {
                "GET": {"handler": self.user_facility.get, "privilege": PRIVILEGE_LEVEL_READ},
                "PATCH": {"handler": self.user_facility.patch, "privilege": PRIVILEGE_LEVEL_ADMIN},
                "POST": {"handler": self.user_facility.post, "privilege": PRIVILEGE_LEVEL_ADMIN},
                "DELETE": {"handler": self.user_facility.delete, "privilege": PRIVILEGE_LEVEL_ADMIN}
            },
            "/api/user/me": {
                "GET": {"handler": self.user_facility.get_me, "privilege": PRIVILEGE_LEVEL_READ}
            },
            "/api/user/me/password": {
                "PATCH": {"handler": self.user_facility.patch_me_password, "privilege": PRIVILEGE_LEVEL_READ}
            }
        }

        # Initialization complete
        self.log.debug("Service layer initialized")

    # METHODS ##########################################################################################################

    def handle_api_request(self, request):
        """
        Handles an API request by delegating to the appropriate handler function
        :param request: The HTTP API request
        :return: The HTTP API response
        """

        # Determine the HTTP method
        try:
            method = request.method
        except AttributeError:
            self.log.error("Attempted to process a request object with no method")
            raise BadRequest("No method in request")

        # Determine the request path
        try:
            path = request.path
        except AttributeError:
            self.log.error("Attempted to process a request object with no path")
            raise BadRequest("No path in request")

        # Search for handler info
        try:
            path_info = self.url_path_to_path_info[path]
        except KeyError:
            self.log.debug("User attempted HTTP <%s> on invalid path <%s>", request.method)
            raise NotFound("No Clauto API method <%s>" % request.path)

        # Check for disallowed HTTP method
        if method not in path_info:
            self.log.debug("HTTP <%s> not permitted for path <%s>", method, path)
            raise MethodNotAllowed("HTTP <%s> not permitted for path <%s>" % (method, path))

        # Determine handler and required privilege level
        handler_info = path_info[method]

        # Check for unimplemented handler
        if handler_info["handler"] is None:
            self.log.debug("Handler for HTTP <%s> on path <%s> is not implemented")
            raise NotImplemented()

        # Renew the session token
        session_token, session_token_dict = self.user_facility.renew(request.cookies.get("JWT"))

        # Only authenticate the user if the handler's required privilege is higher than public
        if handler_info["privilege"] > PRIVILEGE_LEVEL_PUBLIC:

            # A session token is required
            if not session_token:
                self.log.debug("Denying non-login request to privileged resource from client without a session token")
                raise Unauthorized("Not logged in")

            # Get the privilege level from the session token
            try:
                given_privilege_level = session_token_dict["privilege_level"]
            except KeyError:
                self.log.error("Session token without privilege level was somehow renewed. Possible attack.")
                raise Unauthorized("Privilege level not found in session token")

            # Ensure the privilege level is high enough for this handler
            if given_privilege_level < handler_info["privilege"]:
                self.log.debug(
                    "Denying request <%s %s> to insufficiently privileged user <%s>",
                    request.method,
                    request.path,
                    session_token_dict["username"]
                )
                raise Unauthorized("User has insufficient privilege for this action")

        # Extract parameters
        try:
            if request.method == "GET":
                params = request.args
            elif request.method == "PATCH":
                params = request.form
            elif request.method == "POST":
                params = request.form
            elif request.method == "DELETE":
                params = request.form
            else:
                raise MethodNotAllowed()
        except AttributeError:
            raise

        # Find the handler
        handler = handler_info["handler"]

        # Initialize the username to pass to the handler
        if session_token_dict and "username" in session_token_dict:
            username = session_token_dict["username"]
        else:
            username = ""

        # Call the handler
        try:
            # noinspection PyCallingNonCallable
            # PyCharm seems to think handler is a dict. It isn't.
            result = handler(params, username)

        # Only these exceptions should reach Flask
        except BadRequest:
            raise
        except NotFound:
            raise
        except MethodNotAllowed:
            raise
        except Unauthorized:
            raise
        except Forbidden:
            raise
        except NotImplemented:
            raise
        except InternalServerError:
            raise

        # Any other exception becomes an InternalServerError
        except Exception:
            for line in (
                "Handler raised non-HTTP exception. Responding to client with HTTP 500. Traceback is below.\n" +
                traceback.format_exc()
            ).split("\n")[:-1]:
                self.log.error(line)
            raise InternalServerError()

        # If this was a login, put the result (a session token) in the cookie and put "Success" in the response
        if request.path == "/api/user/login":
            cookie = "JWT=%s; Path=/api; Secure; Max-Age=%s" % (result, int(self.config["session_lifetime"]))
            result = "\"Success\""

        # Otherwise, send back the existing session token (which is either None or has been renewed above)
        else:
            cookie = "JWT=%s; Path=/api; Secure; Max-Age=%s" % (session_token, int(self.config["session_lifetime"]))

        # Prepare the response headers
        headers = {}
        if cookie:
            headers["Set-Cookie"] = cookie

        # Return the response
        return Response(
            response=result,
            status=200,
            headers=headers
        )

    # API HANDLERS THAT DON'T FIT IN ANY FACILITY ######################################################################

    # noinspection PyMethodMayBeStatic
    def ping(self, params, username):
        """
        Always returns "pong"
        :param params: Parameters from HTTP request
        :return: "pong"
        """
        return "\"pong\""

    # noinspection PyMethodMayBeStatic
    def ping_slow(self, params, username):
        """
        Always returns "pong", with a delay
        :param params: Parameters from HTTP request
        :return: "pong"
        """
        sleep(5)
        return "\"pong\""
