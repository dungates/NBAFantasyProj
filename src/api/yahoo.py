from pydash.collections import at, key_by, order_by
from pydash.objects import get
from yahoo_fantasy_api import game, league, team
from yahoo_oauth.oauth import OAuth2
from api.nba import fetch_player_projections
from utils.constants import YAHOO_STAT_COEFFS
from utils.helpers import print_fantasy_players


def get_all_league_ids(oauth):
    current_game = game.Game(oauth, "nba")
    league_ids = current_game.league_ids()
    return league_ids


def get_current_league(config_file):
    oauth = OAuth2(None, None, from_file=config_file)
    if not oauth.token_is_valid():
        print("token invalid")
        oauth.refresh_access_token()
    all_league_ids = get_all_league_ids(oauth)
    if not all_league_ids:
        return None
    league_id = all_league_ids[len(all_league_ids) - 1]
    current_league = league.League(oauth, league_id)
    return current_league


def get_team_data(team):
    team_data = {}
    for line in get(team, "team.0"):
        if "team_key" in line:
            team_data["team_key"] = get(line, "team_key")
        elif "name" in line:
            team_data["name"] = get(line, "name")
    return team_data


def get_matchups(league, week=None):
    current_matchups = league.matchups(week)
    matchups = get(current_matchups, "fantasy_content.league.1.scoreboard.0.matchups")
    team_key_tuples = []
    for matchup in matchups.values():
        if not isinstance(matchup, dict):
            continue
        teams = get(matchup, "matchup.0.teams")
        team_1, team_2 = at(teams, "0", "1")
        team_key_tuples.append((get_team_data(team_1), get_team_data(team_2)))
    return team_key_tuples


def fetch_free_agents(league):
    player_projections = key_by(
        fetch_player_projections(YAHOO_STAT_COEFFS), "PLAYER_NAME"
    )

    print("Fetching free agents...")
    free_agents = league.free_agents("")

    players_list = []
    for free_agent in free_agents:
        player_name = free_agent["name"]
        if player_name not in player_projections.keys():
            continue
        player_projection = player_projections[player_name]
        players_list.append(
            {
                "name": player_projection["PLAYER_NAME"],
                "status": free_agent["status"],
                "positions": ",".join(free_agent["eligible_positions"]),
                "age": round(player_projection["AGE"]),
                "games_played": player_projection["GP"],
                "minutes_per_game": round(
                    player_projection["MIN"] / player_projection["GP"],
                    2,
                ),
                "preseason_fp_projection": round(
                    player_projection["FP_PROJECTION_PRESEASON"], 4
                ),
                "current_fp_projection": round(
                    player_projection["FP_PROJECTION_CURRENT"], 4
                ),
                "percent_owned": free_agent["percent_owned"],
            }
        )
    ordered_players_list = order_by(players_list, ["-current_fp_projection"])
    print(f"\nTop free agents")
    print_fantasy_players(ordered_players_list, file_name="free_agents")


def get_roster(oauth, team_key=None):
    current_team = team.Team(oauth, team_key)
    return current_team.roster()


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
