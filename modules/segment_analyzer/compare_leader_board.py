def find_avg_time(segment_tries):
    for attempt in segment_tries:
        print(attempt.moving_time)
        print(type(attempt.moving_time))

        print(attempt.moving_time.days)
        print(type(attempt.moving_time.days))

    return {"days": 3, "seconds": 3, "microseconds": 3}


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
        leader_board_stats["avg_time"] = find_avg_time(leader_board.entries)
    return leader_board_stats
