from constants import SEASON_WEIGHTS, STAT_COEFFS
import json


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


def get_weighted_average(player_season_list):
    total = 0
    divisor = 0
    for index, weight in enumerate(SEASON_WEIGHTS):
        if index == len(player_season_list):
            break
        player_season = player_season_list[index]
        total = total + weight * player_season["FP"]
        divisor = divisor + weight * player_season["GP"]
    return total / divisor


def inject_fantasy_points(player_season_list):
    for player_season in player_season_list:
        player_season["FP"] = get_fantasy_points(player_season)


def write_json(data, filename):
    with open("Data/" + filename + ".json", "w") as json_file:
        json.dump(data, json_file, indent=2)
