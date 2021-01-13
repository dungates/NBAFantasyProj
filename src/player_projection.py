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
from utils import calc_fantasy_points, write_json


num_past_seasons = len(SEASON_WEIGHTS)


def print_roster(roster, name, player_projections):
    print("\n" + name)
    for player in roster:
        fantasy_points_projection = "N/A"
        games_played = 0
        if player["name"] in player_projections.keys():
            fantasy_points_projection = str(
                player_projections[player["name"]]["FANTASY_POINTS_PROJECTION"]
            )
            games_played = player_projections[player["name"]]["GP"]
        print(
            player["selected_position"]
            + "\t"
            + player["name"].ljust(24)
            + "\t"
            + str(games_played)
            + "\t"
            + fantasy_points_projection
        )
    print("\n")


def calc_player_projection(player_stats_list):
    total = 0
    divisor = 0
    for player_stats in player_stats_list:
        total_fantasy_points = calc_fantasy_points(player_stats["stats"])
        average_fantasy_points = total_fantasy_points / player_stats["stats"]["GP"]
        total += player_stats["weight"] * average_fantasy_points
        divisor += player_stats["weight"]
    return total / divisor


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

        player_stats_list = []
        player_stats_list.append({"weight": 1, "stats": player_season_stats})

        if player_id in month_stats.keys():
            player_stats_list.append({"weight": 1, "stats": month_stats[player_id]})

        if player_id in week_stats.keys():
            player_stats_list.append({"weight": 1, "stats": week_stats[player_id]})

        fantasy_points_projection = calc_player_projection(player_stats_list)
        player_projections[player_name] = {
            "PLAYER_NAME": player_name,
            "FANTASY_POINTS_PROJECTION": fantasy_points_projection,
            "GP": player_season_stats["GP"],
        }

    return player_projections


def main():
    player_projections = get_player_projections()
    write_json(
        order_by(player_projections.values(), ["-FANTASY_POINTS_PROJECTION"]),
        "playerProjections",
    )

    print("Fetching fantasy matchups for current week...")
    current_matchups = get_matchups()
    print("Done\n")

    for matchup in current_matchups:
        team1, team2 = matchup
        print("Fetching roster for " + team1["name"] + "...")
        roster1 = get_roster(team1["team_key"])
        print("Fetching roster for " + team2["name"] + "...")
        roster2 = get_roster(team2["team_key"])

        print_roster(roster1, team1["name"], player_projections)
        print_roster(roster2, team2["name"], player_projections)


if __name__ == "__main__":
    main()
