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
def strava():
    if request.method == "GET":
        s = Strava()
        return s.authorized(), 200


@app.route("/strava_segments", methods=["GET"])
def strava_segments():
    if request.method == "GET":
        sw_lat = request.args.get("sw_lat", default=63.321, type=int)
        sw_lng = request.args.get("sw_lng", default=10.168, type=int)
        ne_lat = request.args.get("ne_lat", default=63.465535, type=int)
        ne_lng = request.args.get("ne_lng", default=10.592642, type=int)
        return (
            jsonify(
                Strava().explore_segments(
                    bounds=[sw_lat, sw_lng, ne_lat, ne_lng]
                )
            ),
            200,
        )
