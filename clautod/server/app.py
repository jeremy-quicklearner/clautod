"""
Entry point for clautod
"""

# IMPORTS ##############################################################################################################

# Standard Python modules
import json

# Other Python modules
from flask import Flask
from flask import request
from flask import send_from_directory
from flask import send_file
from flask import render_template
from gevent.pywsgi import WSGIServer
from werkzeug.exceptions import NotFound


# Clauto Common Python modules
from clauto_common.patterns.singleton import Singleton
from clauto_common.util.config import ClautoConfig
from clauto_common.util.log import Log

# Clautod Python modules
from layers.service.general import ClautodServiceLayer

# CONSTANTS ############################################################################################################

# THE FLASK APP ########################################################################################################
clauto_flask_app = Flask(
    "Clauto Server",
    static_folder="/static/"
)


# ROUTES ###############################################################################################################

# Paths beginning with /api are treated as Clauto API endpoints
@clauto_flask_app.route("/api/<path:path>", methods=['GET', 'PATCH', 'POST', 'DELETE'])
def api_path(path):
    return ClautodServiceLayer().handle_api_request(request)

# Paths beginning with /static send back assets from /static
@clauto_flask_app.route("/static/<path:path>", methods=['GET'])
def static_path(path):
    return send_from_directory("/usr/share/clauto/clautod/web/static", path)

# Anything else
@clauto_flask_app.route("/", defaults={'path':''}, methods=['GET'])
@clauto_flask_app.route("/<path:path>", methods=['GET'])
def catch_all_path(path):
    # Look for static assets
    try:
        return static_path(path)

    # If there are no static assets that match, send index.html
    except NotFound:
        return send_file("/usr/share/clauto/clautod/web/index.html")


# HTTP ERRORS ##########################################################################################################

@clauto_flask_app.errorhandler(400)
@clauto_flask_app.errorhandler(404)
@clauto_flask_app.errorhandler(500)
def http_error(error):
    if request.path.startswith("/api/"):
        return error.description, error.code
    return str(error), error.code

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
            log=self.log.logger,  # TODO: Give Flask its own logs
            certfile="/etc/clauto/clautod/clauto-cert.pem",
            keyfile="/etc/clauto/clautod/clauto-pkey.pem"
            )

        # Initialization complete
        self.log.debug("Flask App initialized. Serving...")

        # Start serving
        self.wsgi_server.serve_forever()
