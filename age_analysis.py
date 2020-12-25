import json
from constants import STAT_COEFFS


def get_averages(totals):
    averages = {}
    for key, total in totals.items():
        averages[key] = total / totals["GP"]
    return averages


def get_totals(players):
    totals = {}
    keys = ["GP", "FP"]
    for key in keys + list(STAT_COEFFS.keys()):
        totals[key] = 0
    for player in players:
        player["FP"] = get_fantasy_points(player)
        for key, total in totals.items():
            totals[key] = total + player[key]
    return totals


def get_fantasy_points(player_stats):
    total = 0
    for key, coeff in STAT_COEFFS.items():
        total = total + coeff * player_stats[key]
    return total


def analyze_data(data):
    age_data = {}
    for age in sorted(data.keys()):
        players = data[age]
        totals = get_totals(players)
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
    with open("statsByAge.json", "w") as json_file:
        json.dump(age_data, json_file)


if __name__ == "__main__":
    with open("Data/seasonTotalsByAge.json") as json_file:
        data = json.load(json_file)
        analyze_data(data)