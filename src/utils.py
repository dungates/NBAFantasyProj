import json
from constants import STAT_COEFFS


def calc_fantasy_points(player_season):
    total = 0
    for key, coeff in STAT_COEFFS.items():
        total = total + coeff * player_season[key]
    return total


def write_json(data, filename):
    with open("Data/" + filename + ".json", "w") as json_file:
        json.dump(data, json_file, indent=2)
