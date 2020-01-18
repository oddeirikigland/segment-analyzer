import time

from modules.segment_analyzer.client import Strava
from modules.segment_analyzer.grid_split import (
    smaller_grid_generator,
    create_square_around_point,
)

SIXTEEN_MIN_IN_SEC = 16 * 60
ONE_DAY_IN_SEC = 60 * 60 * 24


def init_populate(token, mongo, big_bound, grid_split=10, activity_type=None):
    s = Strava(token, mongo)
    grid_bounds = smaller_grid_generator(big_bound, grid_split)
    while True:
        for grid in grid_bounds:
            s.find_all_segments_in_area(grid, activity_type=activity_type)

            # Strava API only accept 600 request every 15 minutes and 30000 a day
            if s.strava_api_requests > 550:
                print("\n\nSLEEPING 16 MINUTES\n\n")
                time.sleep(SIXTEEN_MIN_IN_SEC)
                s.reset_api_request_counter()

            if s.strava_daily_api_requests > 29950:
                time.sleep(ONE_DAY_IN_SEC)
                print("\n\nSLEEPING 24 HOURS\n\n")
                s.reset_all_api_request_counter()


def populate_saved_locations(token, mongo, activity_type):
    s = Strava(token, mongo)
    locations = [
        segment for segment in s.db.locations.find({"is_populated": False})
    ]
    for location in locations:
        if s.strava_api_requests < (600 / len(locations)):
            sw_lat, sw_lng, ne_lat, ne_lng = create_square_around_point(
                location["latitude"], location["longitude"]
            )
            print(sw_lat, sw_lng, ne_lat, ne_lng)
            s.find_all_segments_in_area(
                [sw_lat, sw_lng, ne_lat, ne_lng], activity_type=activity_type
            )
            s.db.locations.update_one(
                {"_id": location["_id"]},
                {
                    "$set": {
                        "is_populated": True,
                        "sw_lat": sw_lat,
                        "sw_lng": sw_lng,
                        "ne_lat": ne_lat,
                        "ne_lng": ne_lng,
                    }
                },
                upsert=False,
            )

    return "Updated {} locations".format(len(locations))
