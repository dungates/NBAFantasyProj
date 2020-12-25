from constants import STAT_COEFFS


def get_averages(totals):
    averages = {}
    for key, total in totals.items():
        averages[key] = total / totals["GP"]
    return averages


def get_fantasy_points(player_season):
    total = 0
    for key, coeff in STAT_COEFFS.items():
        total = total + coeff * player_season[key]
    return total


get_season_qualified = (
    lambda player_season: True if player_season["MIN"] >= 1000 else False
)


def inject_fantasy_points(player_season_list):
    for player_season in player_season_list:
        player_season["FP"] = get_fantasy_points(player_season)
