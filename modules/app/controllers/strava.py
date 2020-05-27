import os
import time
from flask import request, jsonify, redirect, url_for
from flask_cors import cross_origin

from modules.app import app, mongo
from modules.segment_analyzer.client import Strava

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URL = os.getenv("REDIRECT_URL") + "strava_authorized"

strava = Strava(mongo=mongo)
strava.token_expires_at = None


def check_token():
    if time.time() > strava.token_expires_at:
        refresh_response = strava.refresh_access_token(
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            refresh_token=strava.refresh_token,
        )
        access_token = refresh_response["access_token"]
        refresh_token = refresh_response["refresh_token"]
        expires_at = refresh_response["expires_at"]
        strava.access_token = access_token
        strava.refresh_token = refresh_token
        strava.token_expires_at = expires_at


@app.route("/strava", methods=["GET"])
@cross_origin()
def read_root():
    if request.method == "GET":
        if strava.token_expires_at:
            check_token()
            sort = request.args.get("sort", default="rank")
            reverse = request.args.get("direction", default="asc") == "desc"
            return strava.get_table(sort, reverse), 200
        else:
            authorize_url = strava.authorization_url(
                client_id=CLIENT_ID, redirect_uri=REDIRECT_URL
            )
            return redirect(authorize_url, code=302)


@app.route("/strava_authorized", methods=["GET"])
@cross_origin()
def get_code():
    if request.method == "GET":
        # state = request.args.get("state", type=str)
        # scope = request.args.get("scope", type=str)
        code = request.args.get("code", type=str)
        token_response = strava.exchange_code_for_token(
            client_id=CLIENT_ID, client_secret=CLIENT_SECRET, code=code
        )
        strava.access_token = token_response["access_token"]
        strava.refresh_token = token_response["refresh_token"]
        strava.token_expires_at = token_response["expires_at"]
        return redirect(url_for("read_root"))


@app.route("/strava_segments", methods=["GET"])
@cross_origin()
def strava_segments():
    if request.method == "GET":
        county_number = request.args.get("county_number", default=0, type=int)
        segment_distance = request.args.get(
            "segment_distance", default=10, type=int
        )
        latitude = request.args.get("latitude", default=63.0, type=float)
        longitude = request.args.get("longitude", default=10.0, type=float)
        activity_view = request.args.get(
            "activity_view", default="All", type=str
        )
        number_of_segments = request.args.get(
            "number_of_segments", default=100, type=int
        )
        strava.location_to_populate(latitude, longitude)
        return (
            jsonify(
                strava.get_easiest_segments_in_area(
                    county_number=county_number,
                    segment_distance=segment_distance,
                    latitude=latitude,
                    longitude=longitude,
                    activity_view=activity_view,
                    number_of_segments=number_of_segments,
                )
            ),
            200,
        )
