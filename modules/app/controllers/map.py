import os
from flask import request, jsonify, json
from flask_cors import cross_origin

from constants import ROOT_DIR
from modules.app import app
from modules import logger


LOG = logger.get_root_logger(
    os.environ.get(__name__),
    filename=os.path.join(ROOT_DIR, "modules/logger/output.log"),
)


@app.route("/map/countyNorway", methods=["GET"])
@cross_origin()
def county_norway():
    if request.method == "GET":
        return (
            jsonify(
                json.load(
                    open("{}/modules/map/countyNorway.json".format(ROOT_DIR))
                )
            ),
            200,
        )
