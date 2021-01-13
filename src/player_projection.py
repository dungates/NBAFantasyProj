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


def print_roster(roster, name):
    print("\n" + name)
    for player in roster:
        print(player["selected_position"] + "\t" + player["name"])
    print("\n")


def get_player_projections():
    print("Fetching current season stats...")
    season_stats = get_current_season_stats("season")

    print("Fetching past month stats...")
    month_stats = get_current_season_stats("month")

    print("Fetching past week stats...")
    week_stats = get_current_season_stats("week")

    player_projections = {}
    for player_id, player_season_stats in season_stats.items():
        player_name = player_season_stats["PLAYER_NAME"]

        stats = []
        stats.append({"weight": 1, "stats": player_season_stats})

        if player_id in month_stats.keys():
            stats.append({"weight": 1, "stats": month_stats[player_id]})

        if player_id in week_stats.keys():
            stats.append({"weight": 1, "stats": week_stats[player_id]})

        player_projections[player_name] = stats

    return player_projections


def main():
    current_week = get_current_week()
    print("Week: " + str(current_week))

    player_projections = get_player_projections()

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
