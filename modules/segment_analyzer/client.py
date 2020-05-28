from datetime import datetime, timedelta
from stravalib.client import Client
from stravalib.exc import RateLimitTimeout, RateLimitExceeded
from stravalib.model import Activity
from threading import Thread, active_count

from modules.segment_analyzer.client_helpers import (
    is_segment_within_range,
    normalize_segments,
    add_prioritize_segment_value,
)
from modules.segment_analyzer.segment_table import (
    SortableTable,
    Segments,
    Segment,
)
from modules.segment_analyzer.compare_leader_board import recieve_leader_board


class Strava(Client):
    def __init__(self, mongo):
        self.db = mongo.db
        self.update_db_time = datetime.strptime(
            "Jun 1 2005  1:33PM", "%b %d %Y %I:%M%p"
        )
        super().__init__()

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

    def location_to_populate(self, latitude, longitude):
        self.db.locations.insert(
            {
                "date": datetime.now(),
                "latitude": latitude,
                "longitude": longitude,
                "is_populated": False,
            }
        )

    def update_user_db(self, activity_limit):
        time_now = datetime.now()
        if (time_now - self.update_db_time).total_seconds() < 10 * 60:
            print("dont update db, recently did")
            return
        else:
            self.update_db_time = time_now
        try:
            athlete = self.get_athlete()
            if not self.db.user_segments.find_one({"user_id": athlete.id}):
                self.db.user_segments.insert(
                    {"user_id": athlete.id, "user_segments": []}
                )

            for activity in self.get_activities(limit=activity_limit):
                activity = self.get_activity(
                    activity_id=activity.id, include_all_efforts=True
                )
                if activity.type not in [Activity.RIDE, Activity.RUN]:
                    continue
                for segment_effort in activity.segment_efforts:
                    segment_id = segment_effort.segment.id

                    if "user_segments" not in self.db.user_segments.find_one(
                        {"user_id": athlete.id},
                        {"user_segments": {"$elemMatch": {"id": segment_id}}},
                    ):
                        # The segment is not stored for this user
                        # TODO: Update segment if long time since stored

                        s = self.get_segment(segment_id=segment_id)
                        leader_board_stats = recieve_leader_board(
                            self.get_segment_leaderboard(segment_id=segment_id)
                        )
                        rank = 0
                        for entry in s.leaderboard.entries:
                            if (
                                str(
                                    athlete.firstname
                                    + " "
                                    + athlete.lastname[0]
                                )
                                in entry.athlete_name
                            ):
                                rank = entry.rank
                                break
                        segment = Segment(
                            id=s.id,
                            name=s.name,
                            rank=rank,
                            activity_type=s.activity_type,
                            distance=s.distance.num,
                            pr_time=s.pr_time or 0,
                            athlete_pr_effort=s.athlete_count / s.effort_count,
                            effort_count=s.effort_count,
                            athlete_count=s.athlete_count,
                            star_count=s.star_count,
                            time_since_best=leader_board_stats[
                                "time_since_best"
                            ],
                            avg_vs_best=leader_board_stats["avg_vs_best"],
                            avg_time=leader_board_stats["avg_time"],
                            best_time=leader_board_stats["best_time"],
                            metric=0,
                        )
                        self.db.user_segments.update_one(
                            {"user_id": athlete.id},
                            {"$push": {"user_segments": segment.__dict__}},
                        )
        except RateLimitTimeout:
            print("RateLimitTimeout")
        except RateLimitExceeded:
            print("RateLimitExceeded")

    def get_table(self, sort, reverse, activity_limit, return_type):
        segments = Segments()
        try:
            athlete = self.get_athlete()
            res = [
                segment["user_segments"]
                for segment in self.db.user_segments.find(
                    {"user_id": athlete.id}
                )
            ]
            if len(res) > 0:
                for segment_values in res[0]:
                    s = Segment(**segment_values)
                    segments.add_segment(s)
        except RateLimitTimeout:
            print("RateLimitTimeout")
        except RateLimitExceeded:
            print("RateLimitExceeded")
        thread = Thread(
            target=self.update_user_db,
            kwargs={"activity_limit": activity_limit},
        )
        thread.start()
        if return_type == "json":
            return segments.get_segments_as_dict()
        table = SortableTable(
            segments.get_sorted_segments(sort, reverse),
            sort_by=sort,
            sort_reverse=reverse,
        )
        return table
