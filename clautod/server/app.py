"""
Entry point for clautod
"""

# IMPORTS ##############################################################################################################

# Standard Python modules

# Other Python modules
from flask import Flask
from flask import request
from gevent.pywsgi import WSGIServer


# Clauto Common Python modules
from clauto_common.patterns.singleton import Singleton
from clauto_common.util.config import ClautoConfig
from clauto_common.util.log import Log

# Clautod Python modules
from layers.service.general import ClautodServiceLayer

# CONSTANTS ############################################################################################################

# THE FLASK APP ########################################################################################################
clauto_flask_app = Flask("Clauto Server")


# ROUTES ###############################################################################################################

# Clauto API
# noinspection PyUnusedLocal
@clauto_flask_app.route("/api/<path:path>", methods=['GET', 'PATCH', 'POST', 'DELETE'])
def api(path):
    return ClautodServiceLayer().handle_api_request(request)


# Clauto Web GUI TODO: Make a route for the web gui

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

        # Initialize service layer
        self.service_layer = ClautodServiceLayer()

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
