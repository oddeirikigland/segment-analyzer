import os
from requests.exceptions import HTTPError
from stravalib.client import Client
from datetime import datetime
import json

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
    max_efforts = max(
        filtered_segments,
        key=lambda item: item["efforts"],
    )["efforts"]
    max_time_since = get_only_seconds(
        max(
            filtered_segments,
            key=lambda item: get_only_seconds(
                item["time_since_best"]
            ),
        )["time_since_best"]
    )
    for x in filtered_segments:
        x.update({
            "normalized_efforts": x["efforts"] / max_efforts,
            "normalized_star_count": x["star_count"] / max_star_count,
            "normalized_time_since": get_only_seconds(x["time_since_best"]) / max_time_since,
        })
    return filtered_segments


def add_prioritize_segment_value(segments):
    for segment in segments:
        segment.update({
            "segment_score": segment["normalized_efforts"] + segment["normalized_star_count"] + segment["normalized_time_since"]
        })
    return segments


def get_county_number(county_name):
    with open('{}/modules/map/countyNumbers.json'.format(ROOT_DIR), 'r') as JSON:
        json_dict = json.load(JSON)
        for county in json_dict["containeditems"]:
            if county["description"] == county_name:
                return county["label"]
    return 0


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

    def get_easiest_segments_in_area(self, bounds, county_number):
        # Todo: Only return segments within area
        segments = []
        if county_number > 0:
            segments = [segment for segment in self.db.segments.find({"county_number": county_number})]
        else:
            segments = [segment for segment in self.db.segments.find()]
        norm_segments = normalize_segments(segments)
        prio_segments = add_prioritize_segment_value(norm_segments)
        sorted_segments = sorted(prio_segments, key=lambda k: k['segment_score'])
        ten_easiest = sorted_segments[:10]
        color = 100
        for segment in ten_easiest:
            segment.update({"color": color})
            color -= 10
        return ten_easiest

    def find_all_segments_in_area(self, bounds):
        segments_in_bound = self.explore_segments(bounds)
        if segments_in_bound >= 10 and self.strava_api_requests < 550:
            new_grid_west, new_grid_east = split_bound_area(bounds)
            self.find_all_segments_in_area(new_grid_west)
            self.find_all_segments_in_area(new_grid_east)

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
                self.add_segment_details(segment["_id"])
        return len(filtered_segments)
