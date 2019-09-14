import os
from flask import request, jsonify

from constants import ROOT_DIR
from modules.app import app, mongo
from modules import logger
from modules.segment_analyzer.client import Strava


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
def strava_segments():
    if request.method == "GET":
        sw_lat = request.args.get("sw_lat", default=63.321, type=int)
        sw_lng = request.args.get("sw_lng", default=10.168, type=int)
        ne_lat = request.args.get("ne_lat", default=63.465535, type=int)
        ne_lng = request.args.get("ne_lng", default=10.592642, type=int)
        return (
            jsonify(
                Strava(token="", mongo=mongo).get_all_segments_in_area(
                    bounds=[sw_lat, sw_lng, ne_lat, ne_lng]
                )
            ),
            200,
        )


@app.route("/strava_update_db", methods=["GET"])
def strava_update_db():
    if request.method == "GET":
        code = request.args.get("code")
        sw_lat = request.args.get("sw_lat", default=63.321, type=int)
        sw_lng = request.args.get("sw_lng", default=10.168, type=int)
        ne_lat = request.args.get("ne_lat", default=63.465535, type=int)
        ne_lng = request.args.get("ne_lng", default=10.592642, type=int)
        Strava(token=code, mongo=mongo).find_all_segments_in_area(
            bounds=[sw_lat, sw_lng, ne_lat, ne_lng]
        )
        return 1
