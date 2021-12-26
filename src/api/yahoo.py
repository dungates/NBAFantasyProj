from typing import List
from pydash.collections import at, order_by
from pydash.objects import get
from yahoo_fantasy_api import game, league, team
from yahoo_oauth.oauth import OAuth2

from utils.types import FantasyPlayer


class YahooClient:
    def __init__(self, config_path):
        super().__init__()
        oauth = OAuth2(None, None, from_file=config_path)
        if not oauth.token_is_valid():
            print("token invalid")
            oauth.refresh_access_token()
        self.oauth = oauth

    def get_all_league_ids(self):
        current_game = game.Game(self.oauth, "nba")
        league_ids = current_game.league_ids()
        return league_ids

    def get_current_league(self):
        all_league_ids = self.get_all_league_ids()
        if not all_league_ids:
            return None
        league_id = all_league_ids[len(all_league_ids) - 1]
        current_league = league.League(self.oauth, league_id)
        return current_league

    def fetch_matchups(self, league, week=None):
        current_matchups = league.matchups(week)
        matchups = get(
            current_matchups, "fantasy_content.league.1.scoreboard.0.matchups"
        )
        team_key_tuples = []
        for matchup in matchups.values():
            if not isinstance(matchup, dict):
                continue
            teams = get(matchup, "matchup.0.teams")
            team_1, team_2 = at(teams, "0", "1")
            team_key_tuples.append(
                (self.get_team_data(team_1), self.get_team_data(team_2))
            )
        return team_key_tuples

    def fetch_free_agents(self, league: league.League) -> List[FantasyPlayer]:
        free_agents = league.free_agents("")
        players_list = []
        for free_agent in free_agents:
            players_list.append(
                {
                    "name": free_agent["name"],
                    "status": free_agent["status"],
                    "positions": ",".join(free_agent["eligible_positions"]),
                    "selected_position": "",
                    "percent_owned": free_agent["percent_owned"],
                }
            )
        return order_by(players_list, ["-percent_owned"])

    def fetch_roster(self, team_key: str) -> List[FantasyPlayer]:
        current_team = team.Team(self.oauth, team_key)
        current_roster = current_team.roster()
        players_list = []
        for player in current_roster:
            players_list.append(
                {
                    "name": player["name"],
                    "status": player["status"],
                    "positions": ",".join(player["eligible_positions"]),
                    "selected_position": player["selected_position"],
                    "percent_owned": "",
                }
            )
        return players_list

    def get_team_data(self, team_dict):
        team_data = {}
        for line in get(team_dict, "team.0"):
            if "team_key" in line:
                team_data["team_key"] = get(line, "team_key")
            elif "name" in line:
                team_data["name"] = get(line, "name")
        team_data["points_total"] = get(team_dict, "team.1.team_points.total")
        return team_data
