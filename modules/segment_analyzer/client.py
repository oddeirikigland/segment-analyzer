from stravalib.client import Client
from stravalib.exc import RateLimitTimeout, RateLimitExceeded
from datetime import datetime

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


class Strava(Client):
    def __init__(self, mongo):
        self.db = mongo.db
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

    def get_table(self, sort, reverse):
        segments = Segments()
        try:
            for activity in self.get_activities(limit=1):
                print("{0.name} {0.moving_time}".format(activity))
                activity = self.get_activity(
                    activity_id=activity.id, include_all_efforts=True
                )
                for segment_effort in activity.segment_efforts:
                    segment_id = segment_effort.segment.id
                    if not segments.get_segment_by_id(id=segment_id):
                        s = self.get_segment(segment_id=segment_id)
                        rank = 0
                        for entry in s.leaderboard.entries:
                            athlete = self.get_athlete()
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
                        segments.add_segment(
                            Segment(
                                id=s.id,
                                name=s.name,
                                rank=rank,
                                activity_type=s.activity_type,
                                distance=s.distance,
                                pr_time=s.pr_time or 0,
                                athlete_pr_effort=s.athlete_count
                                / s.effort_count,
                                effort_count=s.effort_count,
                                athlete_count=s.athlete_count,
                                star_count=s.star_count,
                            )
                        )
        except RateLimitTimeout:
            print("RateLimitTimeout")
        except RateLimitExceeded:
            print("RateLimitExceeded")

        table = SortableTable(
            segments.get_sorted_segments(sort, reverse),
            sort_by=sort,
            sort_reverse=reverse,
        )
        return table.__html__()
