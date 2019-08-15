from requests.exceptions import HTTPError
from stravalib.client import Client

from modules.segment_analyzer.compare_leader_board import recieve_leader_board


def split_bound_area(bounds):
    sw_lat, sw_lng, ne_lat, ne_lng = bounds
    lat_split_grid =  sw_lat + ((ne_lat - sw_lat) / 2)
    bounds1 = [sw_lat, sw_lng, lat_split_grid, ne_lng]
    bounds2 = [lat_split_grid, sw_lng, ne_lat, ne_lng]
    return bounds1, bounds2


class Strava(Client):
    def __init__(self):
        self.token = ""
        self.all_segments = []
        super(Strava, self).__init__(self.token)

    def authorized(self):
        strava = Client(access_token=self.token)
        try:
            return strava.get_athlete().firstname
        except (HTTPError, AttributeError):
            return False

    def authorize(self):
        strava = Client()
        print(strava)

    def explore_segment_leader_board(self, segment):
        leader_board = super(Strava, self).get_segment_leaderboard(
            segment_id=segment.id
        )
        return recieve_leader_board(leader_board)

    def get_all_segments_in_area(self, bounds):
        self.find_all_segments_in_area(bounds)
        return self.all_segments

    def find_all_segments_in_area(self, bounds):
        segments = self.explore_segments(bounds)
        if len(segments) >= 10:
            new_grid_west, new_grid_east = split_bound_area(bounds)
            self.get_all_segments_in_area(new_grid_west)
            self.get_all_segments_in_area(new_grid_east)
        else:
            self.all_segments += segments


    def explore_segments(
        self, bounds, activity_type=None, min_cat=None, max_cat=None
    ):
        segments = super(Strava, self).explore_segments(
            bounds, activity_type, min_cat, max_cat
        )
        return list(
            map(
                lambda x: {
                    "id": x.id,
                    "name": x.name,
                    "leader_board_stats": self.explore_segment_leader_board(x),
                },
                segments,
            )
        )


if __name__ == "__main__":
    s = Strava()
    res = s.explore_segments(bounds=[63.321, 10.168, 63.465535, 10.592642])
    print(res)
