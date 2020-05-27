from flask_table import Table, Col, LinkCol
from flask import url_for


class SortableTable(Table):
    id = Col("ID")
    name = Col("Name")
    rank = Col("rank")
    activity_type = Col("activity_type")
    distance = Col("distance")
    pr_time = Col("pr_time")
    athlete_pr_effort = Col("athlete_pr_effort")
    effort_count = Col("effort_count")
    athlete_count = Col("athlete_count")
    star_count = Col("star_count")
    # link = LinkCol('Link', 'flask_link', url_kwargs=dict(id='id'), allow_sort=False)
    allow_sort = True

    def sort_url(self, col_key, reverse=False):
        if reverse:
            direction = "desc"
        else:
            direction = "asc"
        return url_for("read_root", sort=col_key, direction=direction)


class Segment(object):
    def __init__(
        self,
        id,
        name,
        rank,
        activity_type,
        distance,
        pr_time,
        athlete_pr_effort,
        effort_count,
        athlete_count,
        star_count,
    ):
        self.id = id
        self.name = name
        self.rank = rank
        self.activity_type = activity_type
        self.distance = distance
        self.pr_time = pr_time
        self.athlete_pr_effort = athlete_pr_effort
        self.effort_count = effort_count
        self.athlete_count = athlete_count
        self.star_count = star_count


class Segments:
    def __init__(self):
        self.segments = []

    def add_segment(self, segment):
        self.segments.append(segment)

    def get_segments(self):
        return self.segments

    def get_sorted_segments(self, sort, reverse=False):
        return sorted(
            self.get_segments(),
            key=lambda x: getattr(x, sort),
            reverse=reverse,
        )

    def get_segment_by_id(self, id):
        segment = [i for i in self.get_segments() if i.id == id]
        if len(segment) > 0:
            return segment[0]
        return None
