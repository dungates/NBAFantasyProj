import json
from constants import STAT_COEFFS
from utils import get_averages, inject_fantasy_points


def analyze_data(data):
    age_data = {}
    for age in sorted(data.keys()):
        player_seasons = data[age]
        inject_fantasy_points(player_seasons)
        totals = get_totals(player_seasons)
        averages = get_averages(totals)
        print(
            age
            + ": "
            + str(averages["FP"])
            + ", "
            + str(totals["FP"])
            + ", "
            + str(totals["GP"])
        )
        age_data[age] = {"totals": totals, "averages": averages}
    write_data(age_data)


def get_totals(player_seasons):
    totals = {}
    keys = ["GP", "FP"]
    for key in keys + list(STAT_COEFFS.keys()):
        totals[key] = 0
    for player_season in player_seasons:
        for key, total in totals.items():
            totals[key] = total + player_season[key]
    return totals


def write_data(age_data):
    with open("Data/statsByAge.json", "w") as json_file:
        json.dump(age_data, json_file)


if __name__ == "__main__":
    with open("Data/seasonTotalsByAge.json") as json_file:
        data = json.load(json_file)
        analyze_data(data)