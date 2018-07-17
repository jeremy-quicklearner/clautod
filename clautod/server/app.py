"""
Entry point for clautod
"""

# IMPORTS ##############################################################################################################

# Standard Python modules

# Other Python modules
from flask import Flask
from gevent.pywsgi import WSGIServer


# Clauto Common Python modules
from clauto_common.patterns.singleton import Singleton
from clauto_common.util.config import ClautoConfig
from clauto_common.util.log import Log

# Clautod Python modules


# CONSTANTS ############################################################################################################

# THE FLASK APP ########################################################################################################
clauto_flask_app = Flask("Clauto Server")


# ROUTES ###############################################################################################################
@clauto_flask_app.route("/ping")  # TODO: Generate the routes dynamically based on a something in the service layer
def hello():
    return "pong"

@clauto_flask_app.route("/login", methods=['GET'])
def login():
    from layers.service.general import ClautodServiceLayer
    svc = ClautodServiceLayer()

    from flask import Response, request
    return Response(svc.user_facility.user_login(request))


# CLASSES ##############################################################################################################

class ClautoFlaskApp(Singleton):

    def __init__(self):
        """
        Constructor for ClautodFlaskApp class
        """

        # Singleton Initialization
        Singleton.__init__(self)
        if Singleton.is_initialized(self):
            return

        # Initialize config
        self.config = ClautoConfig()

        # Initialize logging
        self.log = Log("clautod")
        self.log.debug("Flask App initializing...")

        # Initialize the Flask App
        self.wsgi_server = WSGIServer(
            listener=("0.0.0.0", int(self.config["port"])),
            application=clauto_flask_app,
            log=None,  # TODO: Give Flask its own logs
            certfile="/etc/clauto/clautod/clauto-cert.pem",
            keyfile="/etc/clauto/clautod/clauto-pkey.pem"
            )

        # Initialization complete
        self.log.debug("Flask App initialized. Serving...")

        # Start serving
        self.wsgi_server.serve_forever()
