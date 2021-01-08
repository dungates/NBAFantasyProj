import json
from pydash.numerical import mean, std_deviation
from constants import SEASON_WEIGHTS
from utils import (
    get_season_qualified,
    get_weighted_average,
    inject_fantasy_points,
    write_json,
)


num_past_seasons = len(SEASON_WEIGHTS)


def analyze_data(data):
    ratios = {}
    for player_seasons in data.values():
        num_player_seasons = len(player_seasons)
        if num_player_seasons < num_past_seasons + 1:
            continue

        inject_fantasy_points(player_seasons)
        for i in range(num_past_seasons, num_player_seasons):
            player_season = player_seasons[i]
            if not get_season_qualified(player_season):
                continue

            past_seasons = []
            for j in range(num_past_seasons):
                past_seasons.append(player_seasons[i - j - 1])
            past_average = get_weighted_average(past_seasons)
            if not past_average:
                continue

            player_age = int(player_season["AGE"])
            if player_age not in ratios.keys():
                ratios[player_age] = []

            current_average = player_season["FP"] / player_season["GP"]
            ratios[player_age].append(current_average / past_average)

    write_data(ratios)


def write_data(ratios):
    data = {}
    for age in sorted(ratios.keys()):
        values = ratios[age]
        data[age] = {
            "mean": mean(values),
            "std_deviation": std_deviation(values),
            "sample_size": len(values),
        }
    write_json(data, "playerAgeAverages")


if __name__ == "__main__":
    with open("Data/seasonTotalsByPlayer.json") as json_file:
        data = json.load(json_file)
        analyze_data(data)