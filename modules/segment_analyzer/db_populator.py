import time

from modules.segment_analyzer.client import Strava
from modules.segment_analyzer.grid_split import smaller_grid_generator

SIXTEEN_MIN_IN_SEC = 16 * 60
ONE_DAY_IN_SEC = 60 * 60 * 24


def init_populate(token, mongo, big_bound, grid_split=10):
    s = Strava(token, mongo)
    grid_bounds = smaller_grid_generator(big_bound, grid_split)
    while True:
        for grid in grid_bounds:
            s.find_all_segments_in_area(grid)

            # Strava API only accept 600 request every 15 minutes and 30000 a day
            if s.strava_api_requests > 600:
                print("\n\nSLEEPING 16 MINUTES\n\n")
                time.sleep(SIXTEEN_MIN_IN_SEC)
                s.reset_api_request_counter()

            if s.strava_daily_api_requests > 30000:
                time.sleep(ONE_DAY_IN_SEC)
                print("\n\nSLEEPING 24 HOURS\n\n")
                s.reset_all_api_request_counter()
