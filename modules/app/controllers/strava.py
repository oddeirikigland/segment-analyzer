from flask import request, jsonify
from flask_cors import cross_origin

from modules.app import app, mongo
from modules.segment_analyzer.client import Strava

strava = Strava(mongo=mongo)


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
