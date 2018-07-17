"""
User facility of service layer for Clautod
"""

# IMPORTS ##############################################################################################################

# Standard Python modules

# Other Python modules

# Clauto Common Python modules
from clauto_common.patterns.singleton import Singleton
from clauto_common.util.config import ClautoConfig
from clauto_common.util.log import Log
from clauto_common.exceptions import MissingSubjectException
from clauto_common.exceptions import InvalidCredentialsException

# Clautod Python modules
from layers.logic.general import ClautodLogicLayer
from entities.user import User


# CONSTANTS ############################################################################################################

# CLASSES ##############################################################################################################

class ClautodServiceLayerUser(Singleton):
    """
    Clautod service layer user facility
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

        # Initialize logic layer
        self.logic_layer = ClautodLogicLayer()

        self.log.verbose("Service layer user facility initialized")

    def user_get(self, request):
        # TODO
        pass

    def user_login(self, request):
        """
        Authenticate a login request and respond with a session token
        :param request: The request from Flask
        :return: A response for Flask
        """

        given_user = User(request.args.get("username"), request.args.get("password"))

        try:
            session_token = self.logic_layer.user_facility.user_login(given_user)
        except MissingSubjectException:
            return "User not found"  # TODO
        except InvalidCredentialsException:
            return "Incorrect Password"  # TODO

        return session_token