import os
from requests.exceptions import HTTPError
from stravalib.client import Client

from modules.segment_analyzer.compare_leader_board import recieve_leader_board


def split_bound_area(bounds):
    sw_lat, sw_lng, ne_lat, ne_lng = bounds
    lat_split_grid = sw_lat + ((ne_lat - sw_lat) / 2)
    bounds1 = [sw_lat, sw_lng, lat_split_grid, ne_lng]
    bounds2 = [lat_split_grid, sw_lng, ne_lat, ne_lng]
    return bounds1, bounds2


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
        key=lambda item: item["leader_board_stats"]["efforts"],
    )["leader_board_stats"]["efforts"]
    max_time_since = get_only_seconds(
        max(
            filtered_segments,
            key=lambda item: get_only_seconds(
                item["leader_board_stats"]["time_since_best"]
            ),
        )["leader_board_stats"]["time_since_best"]
    )
    return list(
        map(
            lambda x: {
                "id": x["id"],
                "name": x["name"],
                "normalized_efforts": x["leader_board_stats"]["efforts"]
                / max_efforts,
                "normalized_star_count": x["star_count"] / max_star_count,
                "normalized_time_since": get_only_seconds(
                    x["leader_board_stats"]["time_since_best"]
                )
                / max_time_since,
            },
            filtered_segments,
        )
    )


class Strava(Client):
    def __init__(self, token=""):
        self.token = token
        self.all_segments = []
        super(Strava, self).__init__(self.token)

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
            segment_id=segment.id
        )
        return recieve_leader_board(leader_board)

    def prioritized_segments(self):
        return list(
            map(
                lambda x: {
                    "segment_score": x["normalized_efforts"]
                    + x["normalized_star_count"]
                    + x["normalized_time_since"],
                    "id": x["id"],
                    "name": x["name"],
                },
                self.all_segments,
            )
        )

    def get_all_segments_in_area(self, bounds):
        self.find_all_segments_in_area(bounds)
        return self.prioritized_segments()

    def find_all_segments_in_area(self, bounds):
        segments = self.explore_segments(bounds)
        if len(segments) >= 10:
            new_grid_west, new_grid_east = split_bound_area(bounds)
            self.find_all_segments_in_area(new_grid_west)
            self.find_all_segments_in_area(new_grid_east)
        else:
            self.all_segments += segments

    def explore_segments(
        self, bounds, activity_type=None, min_cat=None, max_cat=None
    ):
        segments = super(Strava, self).explore_segments(
            bounds, activity_type, min_cat, max_cat
        )
        filtered_segments = list(
            map(
                lambda x: {
                    "id": x.id,
                    "name": x.name,
                    "leader_board_stats": self.explore_segment_leader_board(x),
                    "star_count": x.segment.star_count,
                },
                segments,
            )
        )
        return normalize_segments(filtered_segments)


if __name__ == "__main__":
    s = Strava()
    res = s.get_all_segments_in_area(
        bounds=[63.321, 10.168, 63.465535, 10.592642]
    )
    print(res)
