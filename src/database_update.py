from datetime import datetime, timedelta
from nba_api.stats.endpoints import leaguedashplayerstats
from pydash.collections import flat_map
from pydash.objects import get, omit
from api.nba import fetch_current_schedule, get_current_season_full
from utils.sqlite import (
    update_data_table_from_dicts,
    update_data_table_from_stats_response,
)


def update_current_schedule():
    schedule_data = fetch_current_schedule()
    if not schedule_data:
        return

    game_dates = get(schedule_data, "leagueSchedule.gameDates")
    games = flat_map(game_dates, lambda game_date: get(game_date, "games"))
    reg_season_games = filter(lambda game: get(game, "weekNumber") > 0, games)
    game_data = list(
        map(
            lambda game: {
                **omit(game, ["broadcasters", "homeTeam", "awayTeam", "pointsLeaders"]),
                "homeTeamId": get(game, "homeTeam.teamId"),
                "awayTeamId": get(game, "awayTeam.teamId"),
            },
            reg_season_games,
        )
    )
    primary_keys = ["gameId"]
    update_data_table_from_dicts("game_schedule", game_data, primary_keys)


def update_last_totals(season, last_range):
    time_to_subtract = None
    if last_range == "week":
        time_to_subtract = timedelta(days=7)
    elif last_range == "month":
        time_to_subtract = timedelta(days=30.4375)
    else:
        print(f"Invalid last range '{last_range}'")
        return

    print(f"Fetching player stats totals for last {last_range}...")
    date_from = datetime.today() - time_to_subtract
    stats_response = leaguedashplayerstats.LeagueDashPlayerStats(
        season=season, date_from_nullable=date_from
    )

    primary_keys = ["PLAYER_NAME"]
    update_data_table_from_stats_response(
        f"player_last_{last_range}_totals", stats_response, primary_keys
    )


def update_player_season(season):
    print(f"Fetching player stats totals for {season}...")
    totals_response = leaguedashplayerstats.LeagueDashPlayerStats(season=season)

    print(f"Fetching player stats per 100 for {season}...")
    per_100_response = leaguedashplayerstats.LeagueDashPlayerStats(
        season=season, per_mode_detailed="Per100Possessions"
    )

    primary_keys = ["SEASON", "PLAYER_NAME"]
    extra_values = [("SEASON", season)]
    update_data_table_from_stats_response(
        "player_seasons_totals", totals_response, primary_keys, extra_values
    )
    update_data_table_from_stats_response(
        "player_seasons_per_100", per_100_response, primary_keys, extra_values
    )


def update_current_season_stats():
    current_season = get_current_season_full()
    update_player_season(current_season)
    update_last_totals(current_season, "month")
    update_last_totals(current_season, "week")


if __name__ == "__main__":
    update_current_schedule()
    update_current_season_stats()
