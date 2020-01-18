import os
from requests.exceptions import HTTPError
from stravalib.client import Client
from datetime import datetime
import json
from math import cos, asin, sqrt

from constants import ROOT_DIR
from modules.segment_analyzer.compare_leader_board import recieve_leader_board
from modules.segment_analyzer.grid_split import split_bound_area


def get_only_seconds(time_object):
    days_as_sec = time_object["days"] * 3600
    micro_sec_as_sec = time_object["microseconds"] / 1000000
    return days_as_sec + time_object["seconds"] + micro_sec_as_sec


def normalize_segments(filtered_segments):
    max_star_count = max(
        filtered_segments, key=lambda item: item["star_count"]
    )["star_count"]
    max_efforts = max(filtered_segments, key=lambda item: item["efforts"])[
        "efforts"
    ]
    max_time_since = get_only_seconds(
        max(
            filtered_segments,
            key=lambda item: get_only_seconds(item["time_since_best"]),
        )["time_since_best"]
    )
    for x in filtered_segments:
        x.update(
            {
                "normalized_efforts": x["efforts"] / max_efforts,
                "normalized_star_count": x["star_count"] / max_star_count,
                "normalized_time_since": get_only_seconds(x["time_since_best"])
                / max_time_since,
            }
        )
    return filtered_segments


def add_prioritize_segment_value(segments):
    for segment in segments:
        segment.update(
            {
                "segment_score": segment["normalized_efforts"]
                + segment["normalized_star_count"]
                + segment["normalized_time_since"]
            }
        )
    return segments


def get_county_number(county_name):
    with open(
        "{}/modules/map/countyNumbers.json".format(ROOT_DIR), "r"
    ) as JSON:
        json_dict = json.load(JSON)
        for county in json_dict["containeditems"]:
            if county["description"] == county_name:
                return county["label"]
    return 0


def haversine_distance(lat1, lon1, lat2, lon2):
    p = 0.017453292519943295  # Pi/180
    a = (
        0.5
        - cos((lat2 - lat1) * p) / 2
        + cos(lat1 * p) * cos(lat2 * p) * (1 - cos((lon2 - lon1) * p)) / 2
    )
    return 12742 * asin(sqrt(a))


def is_segment_within_range(segment, latitude, longitude, segment_distance):
    try:
        return (
            haversine_distance(
                segment["start_latitude"],
                segment["start_longitude"],
                latitude,
                longitude,
            )
            < segment_distance
        )
    except KeyError:
        return False


class Strava(Client):
    def __init__(self, token, mongo):
        self.token = token
        self.db = mongo.db
        self.all_segments = []
        self.strava_api_requests = 0
        self.strava_daily_api_requests = 0
        super(Strava, self).__init__(self.token)

    def reset_api_request_counter(self):
        self.strava_daily_api_requests += self.strava_api_requests
        self.strava_api_requests = 0

    def reset_all_api_request_counter(self):
        self.strava_daily_api_requests = 0
        self.strava_api_requests = 0

    def authorized(self):
        strava = Client(access_token=self.token)
        try:
            return strava.get_athlete().firstname
        except (HTTPError, AttributeError):
            return False

    def authorize(self):
        client_id = os.environ.get("CLIENT_ID")
        authorize_url = self.authorization_url(
            client_id=client_id,
            redirect_uri="http://127.0.0.1:3000/strava_auth",
        )
        return authorize_url

    def explore_segment_leader_board(self, segment):
        leader_board = super(Strava, self).get_segment_leaderboard(
            segment_id=segment["_id"]
        )
        leader_board_stats = recieve_leader_board(leader_board)
        leader_board_stats["time_info_added"] = datetime.now()
        self.db.segments.update_one(
            {"_id": segment["_id"]}, {"$set": leader_board_stats}, upsert=False
        )

    def add_segment_details(self, segment_id):
        segment = super(Strava, self).get_segment(segment_id)
        coordinates = {
            "start_latitude": segment.start_latitude,
            "start_longitude": segment.start_longitude,
            "end_latitude": segment.end_latitude,
            "end_longitude": segment.end_longitude,
            "activity_type": segment.activity_type,
            "distance": {"value": segment.distance.num},
            "county": segment.state,
            "county_number": get_county_number(segment.state),
            "city": segment.city,
            "country": segment.country,
            "total_elevation_gain": {
                "value": segment.total_elevation_gain.num
            },
            "climb_category": segment.climb_category,
        }
        self.strava_api_requests += 1
        self.db.segments.update_one(
            {"_id": segment_id}, {"$set": coordinates}, upsert=False
        )
        return coordinates["country"] == "Norway"

    def get_easiest_segments_in_area(
        self,
        county_number,
        segment_distance,
        latitude,
        longitude,
        activity_view,
        number_of_segments,
    ):
        query = {}
        if county_number > 0:
            query["county_number"] = county_number
        if activity_view != "All":
            query["activity_type"] = activity_view

        segments = [segment for segment in self.db.segments.find(query)]
        segments = list(
            filter(
                lambda segment: is_segment_within_range(
                    segment, latitude, longitude, segment_distance
                ),
                segments,
            )
        )
        if len(segments) == 0:
            return []
        norm_segments = normalize_segments(segments)
        prio_segments = add_prioritize_segment_value(norm_segments)
        sorted_segments = sorted(
            prio_segments, key=lambda k: k["segment_score"]
        )

        fraq_size = int((number_of_segments / 100) * len(sorted_segments))
        sorted_segments = sorted_segments[:fraq_size]

        color_fraq = 100 / len(sorted_segments)
        color = 100
        for segment in sorted_segments:
            segment.update({"color": color})
            color -= color_fraq
        return sorted_segments

    def find_all_segments_in_area(self, bounds, activity_type):
        segments_in_bound = self.explore_segments(
            bounds, activity_type=activity_type
        )
        if (
            segments_in_bound >= 10
            and self.strava_api_requests < 550
            and self.strava_daily_api_requests < 29950
        ):
            new_grid_west, new_grid_east = split_bound_area(bounds)
            self.find_all_segments_in_area(new_grid_west, activity_type)
            self.find_all_segments_in_area(new_grid_east, activity_type)

    def explore_segments(
        self, bounds, activity_type=None, min_cat=None, max_cat=None
    ):
        segments = super(Strava, self).explore_segments(
            bounds, activity_type, min_cat, max_cat
        )
        filtered_segments = list(
            map(
                lambda x: {
                    "_id": x.id,
                    "name": x.name,
                    "star_count": x.segment.star_count,
                },
                segments,
            )
        )
        self.strava_api_requests += len(filtered_segments) + 1
        for segment in filtered_segments:
            if not self.db.segments.find_one({"_id": segment["_id"]}):
                self.db.segments.insert(segment)
                self.explore_segment_leader_board(segment)
                is_norwegian_segment = self.add_segment_details(segment["_id"])
                if not is_norwegian_segment:
                    self.db.segments.delete_one({"country": {"$ne": "Norway"}})
        return len(filtered_segments)

    def location_to_populate(self, latitude, longitude):
        self.db.locations.insert(
            {
                "date": datetime.now(),
                "latitude": latitude,
                "longitude": longitude,
                "is_populated": False,
            }
        )
