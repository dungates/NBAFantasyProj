from typing import Any, Dict, List
from pydash.collections import key_by
from api.database import get_player_last_totals, get_player_season_totals
from utils.constants import PEAK_AGE
from utils.helpers import calc_fantasy_points, get_current_season, remove_periods


def calc_player_projection(
    player_stats_list: List[Dict[str, Any]], stat_categories: Dict[str, float]
) -> float:
    if not player_stats_list:
        return 0
    total = 0
    divisor = 0
    for player in player_stats_list:
        total_fantasy_points = calc_fantasy_points(player["stats"], stat_categories)
        average_fantasy_points = total_fantasy_points / player["stats"]["GP"]
        total += player["weight"] * average_fantasy_points * player["stats"]["GP"]
        divisor += player["weight"] * player["stats"]["GP"]
    return total / divisor


def get_player_projections(
    fantasy_coeffs: Dict[str, float]
) -> Dict[str, Dict[str, Any]]:
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

        player_season_stats["PLAYER_NAME"] = remove_periods(
            player_season_stats["PLAYER_NAME"]
        )
        player_season_stats["FP"] = calc_fantasy_points(
            player_season_stats, fantasy_coeffs
        )
        player_season_stats["FP_PROJECTION_PRESEASON"] = preseason_projection
        player_season_stats["FP_PROJECTION_CURRENT"] = current_projection

    return key_by(season_stats.values(), "PLAYER_NAME")
