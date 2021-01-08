import json
from nba_api.stats.library.parameters import Season, SeasonYear, SeasonID
from pydash.collections import order_by
from api.nba import (
    get_current_season,
    get_current_season_stats,
    get_past_season_stats,
)
from api.yahoo import get_current_week, get_matchups, get_roster
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


def print_roster(roster, name):
    print("\n" + name)
    for player in roster:
        print(player["selected_position"] + "\t" + player["name"])
    print("\n")


def main():
    current_week = get_current_week()
    print("Week: " + str(current_week))

    print("Fetching current season stats...")
    season_stats = get_current_season_stats("season")
    inject_fantasy_points(season_stats)
    print("Done")

    print("Fetching fantasy matchups for current week...")
    current_matchups = get_matchups()
    print("Done\n")

    for matchup in current_matchups:
        team1, team2 = matchup
        print("Fetching roster for " + team1["name"] + "...")
        roster1 = get_roster(team1["team_key"])
        print("Fetching roster for " + team2["name"] + "...")
        roster2 = get_roster(team2["team_key"])

        print_roster(roster1, team1["name"])
        print_roster(roster2, team2["name"])


if __name__ == "__main__":
    main()
