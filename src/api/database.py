import sqlite3
from nba_api.stats.endpoints import (
    leaguedashplayerstats,
    leaguedashteamstats,
)
from nba_api.stats.library.parameters import MeasureTypeSimple
from pydash.collections import flat_map, key_by
from pydash.objects import get, omit
from api.nba import fetch_current_schedule
from utils.helpers import (
    format_season,
    get_current_season_full,
    get_date_from_last_range,
)
from utils.sqlite import (
    update_data_table_from_dicts,
    update_data_table_from_stats_response,
)


def get_schedule_by_team():
    con = sqlite3.connect("nba.db")
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    results = list(cur.execute("SELECT * FROM game_schedule;"))
    con.close()

    schedule_by_team = {}
    for row in results:
        home_team_id = row["homeTeamId"]
        away_team_id = row["awayTeamId"]
        if home_team_id not in schedule_by_team.keys():
            schedule_by_team[home_team_id] = []
        if away_team_id not in schedule_by_team.keys():
            schedule_by_team[away_team_id] = []
        schedule_by_team[home_team_id].append(row)
        schedule_by_team[away_team_id].append(row)
    return schedule_by_team


def get_player_season_totals(season):
    con = sqlite3.connect("nba.db")
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    full_season = format_season(season)
    results = list(
        cur.execute(
            "SELECT * FROM player_seasons_totals WHERE SEASON=:season;",
            {"season": full_season},
        )
    )
    con.close()
    return key_by(map(dict, results), "PLAYER_ID")


def get_player_last_totals(last_range):
    con = sqlite3.connect("nba.db")
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    table_name = f"player_last_{last_range}_totals"
    results = list(cur.execute(f"SELECT * FROM {table_name};"))
    con.close()
    return key_by(results, "PLAYER_ID")


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


def update_last_totals(last_range):
    print(f"Fetching player stats totals for last {last_range}...")
    current_season = get_current_season_full()
    date_from = get_date_from_last_range(last_range)
    stats_response = leaguedashplayerstats.LeagueDashPlayerStats(
        season=current_season, date_from_nullable=date_from
    )

    primary_keys = ["PLAYER_NAME"]
    update_data_table_from_stats_response(
        f"player_last_{last_range}_totals", stats_response, primary_keys
    )


def update_player_season(season):
    full_season = format_season(season)

    print(f"Fetching player stats totals for {full_season}...")
    totals_response = leaguedashplayerstats.LeagueDashPlayerStats(season=full_season)

    print(f"Fetching player stats per 100 for {full_season}...")
    per_100_response = leaguedashplayerstats.LeagueDashPlayerStats(
        season=full_season, per_mode_detailed="Per100Possessions"
    )

    primary_keys = ["SEASON", "PLAYER_NAME"]
    extra_values = [("SEASON", full_season)]
    update_data_table_from_stats_response(
        "player_seasons_totals", totals_response, primary_keys, extra_values
    )
    update_data_table_from_stats_response(
        "player_seasons_per_100", per_100_response, primary_keys, extra_values
    )


def update_opponent_season_totals(season):
    full_season = format_season(season)

    print(f"Fetching opponent stats totals for {full_season}...")
    totals_response = leaguedashteamstats.LeagueDashTeamStats(
        measure_type_detailed_defense=MeasureTypeSimple.opponent, season=full_season
    )

    primary_keys = ["SEASON", "TEAM_ID"]
    extra_values = [("SEASON", full_season)]
    update_data_table_from_stats_response(
        "opponent_season_totals", totals_response, primary_keys, extra_values
    )


def update_opponent_last_totals(last_range):
    current_season = get_current_season_full()

    print(f"Fetching opponent stats totals for last {last_range}...")
    date_from = get_date_from_last_range(last_range)
    totals_response = leaguedashteamstats.LeagueDashTeamStats(
        measure_type_detailed_defense=MeasureTypeSimple.opponent,
        season=current_season,
        date_from_nullable=date_from,
    )

    primary_keys = ["TEAM_ID"]
    update_data_table_from_stats_response(
        f"opponent_last_{last_range}_totals", totals_response, primary_keys
    )
