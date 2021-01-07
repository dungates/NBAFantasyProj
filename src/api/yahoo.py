from pydash.collections import at, order_by
from pydash.objects import get
from yahoo_fantasy_api import game, league, team
from yahoo_oauth import OAuth2

oauth = OAuth2(None, None, from_file="yahooAuth.json")


def get_current_league():
    current_game = game.Game(oauth, "nba")
    league_ids = current_game.league_ids()
    if not league_ids:
        return None
    league_id = league_ids[len(league_ids) - 1]
    current_league = league.League(oauth, league_id)
    return current_league


def get_current_week():
    current_league = get_current_league()
    return current_league.current_week()


def get_stat_categories():
    current_league = get_current_league()
    print(current_league)
    stat_categories = current_league.stat_categories()
    return stat_categories


def get_free_agents():
    current_league = get_current_league()
    players = current_league.free_agents("Util")
    return players


def get_team_key(team):
    team_data = get(team, "team.0")
    for line in team_data:
        if "team_key" in line:
            return get(line, "team_key")
    return None


def get_matchups(week=None):
    current_league = get_current_league()
    current_matchups = current_league.matchups(week)
    matchups = get(current_matchups, "fantasy_content.league.1.scoreboard.0.matchups")
    team_key_tuples = []
    for matchup in matchups.values():
        if not isinstance(matchup, dict):
            continue
        teams = get(matchup, "matchup.0.teams")
        team_1, team_2 = at(teams, "0", "1")
        team_key_tuples.append((get_team_key(team_1), get_team_key(team_2)))
    return team_key_tuples


def get_roster(team_key=None):
    current_team = team.Team(oauth, team_key)
    return current_team.roster()
