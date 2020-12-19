from yahoo_fantasy_api import game, league, team
from yahoo_oauth import OAuth2

oauth = OAuth2(None, None, from_file="yahooAuth.json")


def get_league_id():
    current_game = game.Game(oauth, "nba")
    league_ids = current_game.league_ids()
    if not league_ids:
        return None
    return league_ids[len(league_ids) - 1]


def get_team_key(team):
    team_data = team["team"][0]
    for line in team_data:
        if "team_key" in line:
            return line["team_key"]
    return None


def get_matchups(week):
    league_id = get_league_id()
    current_league = league.League(oauth, league_id)
    matchups = current_league.matchups(week)
    matchups_dict = matchups["fantasy_content"]["league"][1]["scoreboard"]["0"][
        "matchups"
    ]
    team_key_tuples = []
    for key, value in matchups_dict.items():
        if not isinstance(value, dict):
            continue
        teams_dict = value["matchup"]["0"]["teams"]
        team_key_tuples.append(
            (get_team_key(teams_dict["0"]), get_team_key(teams_dict["1"]))
        )
    return team_key_tuples
