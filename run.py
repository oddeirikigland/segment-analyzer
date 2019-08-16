""" index file for REST APIs using Flask """
import os
import sys
import requests
from flask import jsonify, make_response, send_from_directory
from dotenv import load_dotenv

from constants import ROOT_DIR
from modules import logger
from modules.app import app

load_dotenv()

# Create a logger object to log the info and debug
LOG = logger.get_root_logger(
    os.environ.get("ROOT_LOGGER", "root"),
    filename=os.path.join(ROOT_DIR, "modules/logger/output.log"),
)

# Port variable to run the server on.
PORT = os.environ.get("PORT")


@app.errorhandler(404)
def not_found(error):
    """ error handler """
    LOG.error(error)
    return make_response(jsonify({"error": "Not found"}), 404)


@app.route("/")
def index():
    """ static files serve """
    return send_from_directory("pages", "index.html")


@app.route("/<path:path>")
def static_proxy(path):
    """ static folder serve """
    file_name = path.split("/")[-1]
    dir_name = os.path.join("pages", "/".join(path.split("/")[:-1]))
    return send_from_directory(dir_name, file_name)


if __name__ == "__main__":
    LOG.info("running environment: %s", os.environ.get("ENV"))
    app.config["ENV"] = os.environ.get("ENV")
    app.config["DEBUG"] = (
        os.environ.get("ENV") == "development"
    )  # Debug mode if development env
    app.run(host="0.0.0.0", port=int(PORT))  # Run the app
