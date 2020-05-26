from math import cos, asin, sqrt


def get_only_seconds(time_object):
    days_as_sec = time_object["days"] * 3600
    micro_sec_as_sec = time_object["microseconds"] / 1000000
    return days_as_sec + time_object["seconds"] + micro_sec_as_sec


def normalize_segments(filtered_segments):
    max_star_count = max(
        filtered_segments, key=lambda item: item["star_count"]
    )["star_count"]
    max_efforts = max(filtered_segments, key=lambda item: item["efforts"])[
        "efforts"
    ]
    max_time_since = get_only_seconds(
        max(
            filtered_segments,
            key=lambda item: get_only_seconds(item["time_since_best"]),
        )["time_since_best"]
    )
    for x in filtered_segments:
        x.update(
            {
                "normalized_efforts": x["efforts"] / max_efforts,
                "normalized_star_count": x["star_count"] / max_star_count,
                "normalized_time_since": get_only_seconds(x["time_since_best"])
                / max_time_since,
            }
        )
    return filtered_segments


def add_prioritize_segment_value(segments):
    for segment in segments:
        segment.update(
            {
                "segment_score": segment["normalized_efforts"]
                + segment["normalized_star_count"]
                + segment["normalized_time_since"]
            }
        )
    return segments


def haversine_distance(lat1, lon1, lat2, lon2):
    p = 0.017453292519943295  # Pi/180
    a = (
        0.5
        - cos((lat2 - lat1) * p) / 2
        + cos(lat1 * p) * cos(lat2 * p) * (1 - cos((lon2 - lon1) * p)) / 2
    )
    return 12742 * asin(sqrt(a))


def is_segment_within_range(segment, latitude, longitude, segment_distance):
    try:
        return (
            haversine_distance(
                segment["start_latitude"],
                segment["start_longitude"],
                latitude,
                longitude,
            )
            < segment_distance
        )
    except KeyError:
        return False
