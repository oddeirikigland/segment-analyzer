from requests.exceptions import HTTPError
from stravalib.client import Client

from modules.segment_analyzer.compare_leader_board import recieve_leader_board


class Strava(Client):
    def __init__(self):
        self.token = ""
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
    res = s.explore_segments(bounds=[59.9, 10.7, 59.95, 11.04])
    print(res)
