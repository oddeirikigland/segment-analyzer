from stravalib.client import Client
from datetime import datetime

from modules.segment_analyzer.client_helpers import (
    is_segment_within_range,
    normalize_segments,
    add_prioritize_segment_value,
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

    def get_table(self):
        return {"asd": 3333}
