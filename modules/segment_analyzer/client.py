from requests.exceptions import HTTPError
from stravalib.client import Client


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
                    "climb_category": x.climb_category,
                    "climb_category_desc": x.climb_category_desc,
                    "avg_grade": x.avg_grade,
                    "start_latlng": x.start_latlng,
                    "end_latlng": x.end_latlng,
                    "elev_difference": {
                        "num": x.elev_difference.num,
                        "unit": x.elev_difference.unit.specifier,
                    },
                    "distance": {
                        "num": x.distance.num,
                        "unit": x.distance.unit.specifier,
                    },
                    "points": x.points,
                    "starred": x.starred,
                },
                segments,
            )
        )


if __name__ == "__main__":
    s = Strava()
    res = s.explore_segments(bounds=[59.9, 10.7, 59.95, 11.04])
    print(res)
