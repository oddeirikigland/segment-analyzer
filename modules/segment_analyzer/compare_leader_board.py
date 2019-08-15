from datetime import datetime

def find_avg_time(segment_tries):
    days_used, seconds_used, microseconds_used = [], [], []
    for attempt in segment_tries:
        days_used.append(attempt.moving_time.days)
        seconds_used.append(attempt.moving_time.seconds)
        microseconds_used.append(attempt.moving_time.microseconds)
    return {"days": (sum(days_used)/len(days_used)), "seconds": (sum(seconds_used)/len(seconds_used)), "microseconds": (sum(microseconds_used)/len(microseconds_used))}

def relative_dist_leader_avg(best_time, avg_time):
    # assumes that days and microseconds are not important
    return (avg_time["seconds"] - best_time["seconds"]) / best_time["seconds"]


def get_time_since_record(start_date):
    now = datetime.now(start_date.tzinfo)
    time_diff = now - start_date
    return {
        "days": time_diff.days,
        "seconds": time_diff.seconds,
        "microseconds": time_diff.microseconds
    }


def recieve_leader_board(leader_board):
    leader_board_stats = {}
    effort_count = leader_board.effort_count
    if effort_count > 0:
        best_time = {
            "days": leader_board.entries[0].moving_time.days,
            "seconds": leader_board.entries[0].moving_time.seconds,
            "microseconds": leader_board.entries[0].moving_time.microseconds,
        }
        leader_board_stats["best_time"] = best_time
        avg_time = find_avg_time(leader_board.entries)
        leader_board_stats["avg_time"] = avg_time
        leader_board_stats["avg_vs_best"] = relative_dist_leader_avg(best_time, avg_time)
        leader_board_stats["time_since_best"] = get_time_since_record(leader_board.entries[0].start_date)
        leader_board_stats["efforts"] = effort_count
    return leader_board_stats
