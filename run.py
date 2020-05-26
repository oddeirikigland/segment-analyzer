""" index file for REST APIs using Flask """
import os
from flask import send_from_directory
from dotenv import load_dotenv

load_dotenv()

from modules.app import app


@app.errorhandler(404)
def not_found(error):
    """ error handler """
    return send_from_directory("pages", "404.html")


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
