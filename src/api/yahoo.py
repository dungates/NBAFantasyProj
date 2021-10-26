from pydash.collections import at
from pydash.objects import get
from yahoo_fantasy_api import game, league, team


def get_current_league(oauth):
    current_game = game.Game(oauth, "nba")
    league_ids = current_game.league_ids()
    if not league_ids:
        return None
    league_id = league_ids[len(league_ids) - 1]
    current_league = league.League(oauth, league_id)
    return current_league


def get_current_week(oauth):
    current_league = get_current_league(oauth)
    return current_league.current_week()


def get_stat_categories(oauth):
    current_league = get_current_league(oauth)
    stat_categories = current_league.stat_categories()
    return stat_categories


def get_free_agents(oauth):
    current_league = get_current_league(oauth)
    players = current_league.free_agents("Util")
    return players


def get_team_data(team):
    team_data = {}
    for line in get(team, "team.0"):
        if "team_key" in line:
            team_data["team_key"] = get(line, "team_key")
        elif "name" in line:
            team_data["name"] = get(line, "name")
    return team_data


def get_matchups(oauth, week=None):
    current_league = get_current_league(oauth)
    current_matchups = current_league.matchups(week)
    matchups = get(current_matchups, "fantasy_content.league.1.scoreboard.0.matchups")
    team_key_tuples = []
    for matchup in matchups.values():
        if not isinstance(matchup, dict):
            continue
        teams = get(matchup, "matchup.0.teams")
        team_1, team_2 = at(teams, "0", "1")
        team_key_tuples.append((get_team_data(team_1), get_team_data(team_2)))
    return team_key_tuples


def get_roster(oauth, team_key=None):
    current_team = team.Team(oauth, team_key)
    return current_team.roster()
