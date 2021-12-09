from nba_api.stats.endpoints import leaguedashplayerstats
from pydash.collections import flat_map
from pydash.objects import get, omit
import requests

from utils.sqlite import update_data_table, update_data_table_from_dicts


def update_current_schedule():
    try:
        response = requests.get(
            "https://cdn.nba.com/static/json/staticData/scheduleLeagueV2.json"
        )
        data = response.json()
        game_dates = get(data, "leagueSchedule.gameDates")
        games = flat_map(game_dates, lambda game_date: get(game_date, "games"))
        reg_season_games = filter(lambda game: get(game, "weekNumber") > 0, games)
        game_data = list(
            map(
                lambda game: {
                    **omit(
                        game, ["broadcasters", "homeTeam", "awayTeam", "pointsLeaders"]
                    ),
                    "homeTeamId": get(game, "homeTeam.teamId"),
                    "awayTeamId": get(game, "awayTeam.teamId"),
                },
                reg_season_games,
            )
        )
        primary_keys = ["gameId"]
        update_data_table_from_dicts("game_schedule", game_data, primary_keys)
    except TimeoutError:
        print("Unable to fetch schedule data")


def update_season_stats(season):
    stats_response = leaguedashplayerstats.LeagueDashPlayerStats(season=season)

    data = get(stats_response, "data_sets.0.data")
    headers = get(data, "headers")
    data_rows = get(data, "data")
    if not len(data_rows):
        return

    primary_keys = ["SEASON", "PLAYER_NAME"]
    extra_values = [("SEASON", season)]
    update_data_table("test_table", headers, data_rows, primary_keys, extra_values)


if __name__ == "__main__":
    update_current_schedule()
