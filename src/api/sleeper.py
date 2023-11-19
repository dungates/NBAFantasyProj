import json
from typing import List
import requests
from utils.helpers import get_current_season
from utils.types import FantasyPlayer


class SleeperClient:
    def __init__(self, config_path):
        super().__init__()
        with open(config_path) as file:
            data = json.load(file)
            username = data["username"]
            response = requests.get(f"https://api.sleeper.app/v1/user/{username}")
            body = response.json()
            user_id = body["user_id"]
            print(f"User ID: {user_id}")
            self.user_id = user_id

    def fetch_all_league_ids(self):
        current_season = get_current_season()
        response = requests.get(
            f"https://api.sleeper.app/v1/user/{self.user_id}/leagues/nba/{current_season - 1}"
        )
        return list(map(lambda league: league["league_id"], response.json()))

    def fetch_league(league_id):
        response = requests.get(f"https://api.sleeper.app/v1/league/{league_id}")
        return response.json()

    def fetch_rosters(self, league_id):
        if self.rosters:
            return self.rosters
        response = requests.get(
            f"https://api.sleeper.app/v1/league/{league_id}/rosters"
        )
        self.rosters = response.json()
        return self.rosters

    def fetch_matchups(self, league_id, week=None):
        response = requests.get(
            f"https://api.sleeper.app/v1/league/{league_id}/matchups/{week}"
        )
        return response.json()

    def get_roster(self, owner_id):
        rosters = self.fetch_rosters()
        for roster in rosters:
            if roster["owner_id"] == owner_id:
                return roster
        return None

    def get_current_league(self):
        all_league_ids = self.fetch_all_league_ids()
        if not all_league_ids:
            return None
        league_id = all_league_ids[len(all_league_ids) - 1]
        return self.fetch_league(league_id)

    def get_free_agents(self, league_id) -> List[FantasyPlayer]:
        players_list = []
        return players_list

    def get_team_data(self, team_dict):
        team_data = {}
        return team_data
