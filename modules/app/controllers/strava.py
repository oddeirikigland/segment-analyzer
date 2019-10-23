import os
from flask import request, jsonify
from flask_cors import cross_origin

from constants import ROOT_DIR
from modules.app import app, mongo
from modules import logger
from modules.segment_analyzer.client import Strava
from modules.segment_analyzer.db_populator import init_populate


LOG = logger.get_root_logger(
    os.environ.get(__name__),
    filename=os.path.join(ROOT_DIR, "modules/logger/output.log"),
)


@app.route("/strava_auth", methods=["GET"])
def strava_auth():
    if request.method == "GET":
        s = Strava()
        return jsonify(s.authorized(), 200)


@app.route("/strava_log_in", methods=["GET"])
def strava_log_in():
    if request.method == "GET":
        s = Strava()
        return s.authorize(), 200


@app.route("/strava_segments", methods=["GET"])
@cross_origin()
def strava_segments():
    if request.method == "GET":
        sw_lat = request.args.get("sw_lat", default=63.321, type=float)
        sw_lng = request.args.get("sw_lng", default=10.168, type=float)
        ne_lat = request.args.get("ne_lat", default=63.465535, type=float)
        ne_lng = request.args.get("ne_lng", default=10.592642, type=float)
        county_number = request.args.get("county_number", default=0, type=int)
        return (
            jsonify(
                Strava(token="", mongo=mongo).get_easiest_segments_in_area(
                    bounds=[sw_lat, sw_lng, ne_lat, ne_lng],
                    county_number=county_number,
                )
            ),
            200,
        )


@app.route("/strava_update_db", methods=["GET"])
def strava_update_db():
    if request.method == "GET":
        code = request.args.get("code")
        sw_lat = request.args.get("sw_lat", default=63.321, type=float)
        sw_lng = request.args.get("sw_lng", default=10.168, type=float)
        ne_lat = request.args.get("ne_lat", default=63.465535, type=float)
        ne_lng = request.args.get("ne_lng", default=10.592642, type=float)
        Strava(token=code, mongo=mongo).find_all_segments_in_area(
            bounds=[sw_lat, sw_lng, ne_lat, ne_lng]
        )
        return "Success"


@app.route("/strava_populate_norway_db", methods=["GET"])
def strava_populate_norway_db():
    if request.method == "GET":
        code = request.args.get("code")
        init_populate(
            code,
            mongo,
            [58.157935, 2.854579, 71.255612, 31.759905],
            grid_split=1000,
        )
        return "Success"
