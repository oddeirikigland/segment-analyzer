import time

from modules.segment_analyzer.client import Strava
from modules.app import mongo

SIXTEEN_MIN_IN_SEC = 16*60
ONE_DAY_IN_SEC = 60*60*24


def init_populate(token, bigBound):
    s = Strava(token, mongo)

    while True:
        s.find_all_segments_in_area(bigBound)

        # Strava API only accept 600 request every 15 minutes
        time.sleep(SIXTEEN_MIN_IN_SEC)
        s.reset_api_request_counter()

        if s.strava_daily_api_requests > 30000:  # Todo: check if this number is correct
            time.sleep(ONE_DAY_IN_SEC)
            s.reset_all_api_request_counter()


def main():
    init_populate("", [63.321, 10.168, 63.465535, 10.592642])



if __name__ == '__main__':
    main()
