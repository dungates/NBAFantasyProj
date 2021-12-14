from datetime import datetime, timedelta
from functools import reduce
import sqlite3
from nba_api.stats.endpoints import leaguedashplayerstats
from pydash.collections import flat_map, key_by
from pydash.objects import get, omit
from api.nba import fetch_current_schedule
from utils.constants import PEAK_AGE
from utils.helpers import (
    format_season,
    get_current_season,
    get_current_season_full,
    remove_periods,
)
from utils.player_projection import calc_player_projection
from utils.sqlite import (
    update_data_table_from_dicts,
    update_data_table_from_stats_response,
)


def schedule_row_reducer(acc, row):
    home_team_id = row["homeTeamId"]
    away_team_id = row["awayTeamId"]
    if home_team_id not in acc.keys():
        acc[home_team_id] = []
    if away_team_id not in acc.keys():
        acc[away_team_id] = []
    acc[home_team_id].append(row)
    acc[away_team_id].append(row)
    return acc


def get_schedule_by_team():
    con = sqlite3.connect("nba.db")
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    results = list(cur.execute("SELECT * FROM game_schedule;"))
    con.close()
    return reduce(schedule_row_reducer, results, {})


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


def get_player_projections(fantasy_coeffs):
    current_season = get_current_season()
    season_stats_3 = get_player_season_totals(current_season - 3)
    season_stats_2 = get_player_season_totals(current_season - 2)
    season_stats_1 = get_player_season_totals(current_season - 1)
    season_stats = get_player_season_totals(current_season)
    month_stats = get_player_last_totals("month")
    week_stats = get_player_last_totals("week")

    for player_id, player_season_stats in season_stats.items():
        prev_season_stats = []
        if player_id in season_stats_3.keys():
            prev_season_stats.append({"weight": 1, "stats": season_stats_3[player_id]})
        if player_id in season_stats_2.keys():
            prev_season_stats.append({"weight": 2, "stats": season_stats_2[player_id]})
        if player_id in season_stats_1.keys():
            prev_season_stats.append({"weight": 5, "stats": season_stats_1[player_id]})
        age_adjustment = 1 + 0.015 * (PEAK_AGE - player_season_stats["AGE"])
        preseason_projection = age_adjustment * calc_player_projection(
            prev_season_stats, fantasy_coeffs
        )

        current_season_stats = []
        current_season_stats.append({"weight": 1, "stats": player_season_stats})
        if player_id in month_stats.keys():
            current_season_stats.append({"weight": 3, "stats": month_stats[player_id]})
        if player_id in week_stats.keys():
            current_season_stats.append({"weight": 10, "stats": week_stats[player_id]})
        current_projection = calc_player_projection(
            current_season_stats, fantasy_coeffs
        )

        player_season_stats["FP_PROJECTION_PRESEASON"] = preseason_projection
        player_season_stats["FP_PROJECTION_CURRENT"] = current_projection
        player_season_stats["PLAYER_NAME"] = remove_periods(
            player_season_stats["PLAYER_NAME"]
        )

    return key_by(season_stats.values(), "PLAYER_NAME")


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
    time_to_subtract = None
    if last_range == "week":
        time_to_subtract = timedelta(days=7)
    elif last_range == "month":
        time_to_subtract = timedelta(days=30.4375)
    else:
        print(f"Invalid last range '{last_range}'")
        return

    print(f"Fetching player stats totals for last {last_range}...")
    current_season = get_current_season_full()
    date_from = datetime.today() - time_to_subtract
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
