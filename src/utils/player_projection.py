def calc_fantasy_points(player_season, stat_categories):
    total = 0
    for key, coeff in stat_categories.items():
        total = total + coeff * player_season[key]
    return total


def calc_player_projection(player_stats_list, stat_categories):
    if not player_stats_list:
        return 0
    total = 0
    divisor = 0
    for player in player_stats_list:
        total_fantasy_points = calc_fantasy_points(player["stats"], stat_categories)
        average_fantasy_points = total_fantasy_points / player["stats"]["GP"]
        total += player["weight"] * average_fantasy_points * player["stats"]["GP"]
        divisor += player["weight"] * player["stats"]["GP"]
    return total / divisor
