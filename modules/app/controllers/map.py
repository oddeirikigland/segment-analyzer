from flask import request, jsonify, json
from flask_cors import cross_origin

from constants import ROOT_DIR
from modules.app import app


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
