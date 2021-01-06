import json
from nba_api.stats.library.parameters import Season, SeasonYear, SeasonID
from pydash.collections import order_by
from api.nba import get_current_season, get_player_season_stats
from constants import SEASON_WEIGHTS
from utils import get_weighted_average, inject_fantasy_points, write_json


num_past_seasons = len(SEASON_WEIGHTS)


def get_player_stats(name):
    with open("Data/seasonTotalsByPlayer.json") as json_file:
        data = json.load(json_file)
        for player_season_list in data.values():
            if player_season_list[0]["PLAYER_NAME"].lower() == name.lower():
                return player_season_list
    return None


def print_season(age, fantasy_ppg, games_played):
    print(str(age) + "\t" + str(round(fantasy_ppg, 4)) + "\t" + str(games_played))


def main():
    current_season = get_current_season()
    print(current_season)

    season_stats = get_player_season_stats(current_season, 1)

    inject_fantasy_points(season_stats)

    order_by(season_stats, ["-FP"])

    write_json(season_stats, "currentSeasonStats")

    # print("Age" + "\t" + "FP/G" + "\t" + "GP")
    # for player_season in player_season_list:
    #     fantasy_ppg = player_season["FP"] / player_season["GP"]
    #     print_season(player_season["AGE"], fantasy_ppg, player_season["GP"])

    # past_seasons = player_season_list[-num_past_seasons:]
    # past_seasons.reverse()

    # weighted_average = get_weighted_average(past_seasons)
    # print("\nProjected FP/G for next season: " + str(weighted_average))


if __name__ == "__main__":
    main()
