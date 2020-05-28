from datetime import datetime


def time_as_seconds(time_dict):
    return (
        time_dict["days"] * 3600
        + time_dict["seconds"]
        + time_dict["microseconds"] / 1000
    )


def find_avg_time(segment_tries):
    days_used, seconds_used, microseconds_used = [], [], []
    for attempt in segment_tries:
        days_used.append(attempt.moving_time.days)
        seconds_used.append(attempt.moving_time.seconds)
        microseconds_used.append(attempt.moving_time.microseconds)
    return {
        "days": (sum(days_used) / len(days_used)),
        "seconds": (sum(seconds_used) / len(seconds_used)),
        "microseconds": (sum(microseconds_used) / len(microseconds_used)),
    }


def relative_dist_leader_avg(best_time, avg_time):
    # assumes that days and microseconds are not important
    return (avg_time["seconds"] - best_time["seconds"]) / best_time["seconds"]


def get_time_since_record(start_date):
    now = datetime.now(start_date.tzinfo)
    time_diff = now - start_date
    return {
        "days": time_diff.days,
        "seconds": time_diff.seconds,
        "microseconds": time_diff.microseconds,
    }


def recieve_leader_board(leader_board):
    leader_board_stats = {}
    leader_board_stats["avg_vs_best"] = 0
    leader_board_stats["best_time"] = 0
    leader_board_stats["avg_time"] = 0
    leader_board_stats["time_since_best"] = 0

    effort_count = leader_board.effort_count
    if effort_count > 0:
        best_time = {
            "days": leader_board.entries[0].moving_time.days,
            "seconds": leader_board.entries[0].moving_time.seconds,
            "microseconds": leader_board.entries[0].moving_time.microseconds,
        }
        avg_time = find_avg_time(leader_board.entries)
        leader_board_stats["avg_vs_best"] = relative_dist_leader_avg(
            best_time, avg_time
        )
        leader_board_stats["best_time"] = time_as_seconds(best_time)
        leader_board_stats["avg_time"] = time_as_seconds(avg_time)
        leader_board_stats["time_since_best"] = time_as_seconds(
            get_time_since_record(leader_board.entries[0].start_date)
        )
    return leader_board_stats
