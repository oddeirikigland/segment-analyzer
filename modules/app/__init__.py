import os
import json
import datetime
from bson.objectid import ObjectId
from flask import Flask
from flask_cors import CORS
from flask_pymongo import PyMongo
from constants import ROOT_DIR


class JSONEncoder(json.JSONEncoder):
    """ extend json-encoder class"""

    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        if isinstance(o, datetime.datetime):
            return str(o)
        return json.JSONEncoder.default(self, o)


# create the flask object
app = Flask(__name__, template_folder="{}/modules/app/pages".format(ROOT_DIR))
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")

cors = CORS(app)
app.config["CORS_HEADERS"] = "Content-Type"

# add mongo url to flask config, so that flask_pymongo can use it to make connection
app.config["MONGO_URI"] = os.environ.get("DB")
mongo = PyMongo(app, retryWrites=False)

# use the modified encoder class to handle ObjectId & datetime object while jsonifying the response.
app.json_encoder = JSONEncoder

from modules.app.controllers import *
