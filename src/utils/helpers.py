from datetime import datetime, timedelta
import json
import os
import re
import sqlite3
from types import FunctionType
from typing import Any, Dict, List, Tuple
import pytz
from utils.types import FantasyPlayer, FantasyPlayerProjection
from .constants import DAYS_OF_WEEK, LEAGUE_TYPES


def get_weekly_days_string(
    games: List[sqlite3.Row], weeks_from_now: int = 0
) -> List[str]:
    start_time = get_start_of_week(weeks_from_now)
    end_time = get_end_of_week(weeks_from_now)
    game_days = []
    for game in games:
        game_time = iso_8601_to_unix(game["gameDateTimeUTC"])
        if start_time < game_time and game_time < end_time:
            game_days.append(game["day"])
    days = ""
    for day in DAYS_OF_WEEK.keys():
        char = DAYS_OF_WEEK[day] if day in game_days else " "
        days += char
    return days


def get_days_string(games: List[sqlite3.Row], extra_weeks: int = 0) -> str:
    days_string = ""
    for weeks_from_now in range(0, extra_weeks + 1):
        weekly_game_days = get_weekly_days_string(games, weeks_from_now)
        if weeks_from_now > 0:
            days_string += "  "
        days_string += weekly_game_days
    return days_string


def get_config_files() -> List[Tuple[Dict[str, str], os.DirEntry]]:
    files = []
    for type_info in LEAGUE_TYPES.values():
        path = f"config/{type_info['key']}"
        if not os.path.exists(path):
            continue
        with os.scandir(path) as entries:
            for file in entries:
                if file.is_file() and file.name.endswith(".json"):
                    files.append((type_info, file))
    return files


def option_selector(
    prompt: str, data: List[Any], get_label: FunctionType = None
) -> Tuple[int, Any]:
    print(f"\n{prompt}")
    for index, item in enumerate(data):
        label = str(item) if get_label == None else get_label(item)
        print(f"{str(index + 1)}. {label}")
    index = int(input("Enter a number: ")) - 1
    if index >= 0 and index < len(data):
        return (index, data[index])
    else:
        print("Invalid number")
        return option_selector(prompt, data, get_label)


def write_json(data: str, filename: str):
    with open(f"{filename}.json", "w") as json_file:
        json.dump(data, json_file, indent=2)


def write_txt(data: str, filename: str):
    with open(f"Data/{filename}.txt", "w") as txt_file:
        txt_file.write(data)


def remove_periods(str: str) -> str:
    return str.replace(".", "")


def get_current_season() -> int:
    today = datetime.today()
    return today.year if today.month < 9 else today.year + 1


def format_season(season: int) -> str:
    return str(season - 1) + "-" + str(season)[-2:]


def get_current_season_full() -> str:
    current_season = get_current_season()
    return format_season(current_season)


def get_current_time() -> datetime:
    return datetime.now(tz=pytz.timezone("America/Los_Angeles"))


def iso_8601_to_unix(iso: str) -> float:
    formatted_iso = re.sub(r"Z$", "+00:00", iso)
    return datetime.fromisoformat(formatted_iso).timestamp()


def get_start_of_week(weeks_from_now: int = 0) -> float:
    today = get_current_time()
    first_day_of_week = (
        today + timedelta(weeks=weeks_from_now) - timedelta(days=today.weekday())
    )
    return first_day_of_week.replace(
        hour=0, minute=0, second=0, microsecond=0
    ).timestamp()


def get_end_of_week(weeks_from_now: int = 0) -> float:
    today = get_current_time()
    first_day_of_next_week = (
        today + timedelta(weeks=weeks_from_now) + timedelta(days=7 - today.weekday())
    )
    return first_day_of_next_week.replace(
        hour=0, minute=0, second=0, microsecond=0
    ).timestamp()


def get_date_from_last_range(last_range):
    time_to_subtract = None
    if last_range == "week":
        time_to_subtract = timedelta(days=7)
    elif last_range == "month":
        time_to_subtract = timedelta(days=30.4375)
    else:
        print(f"Invalid last range '{last_range}'")
        return None
    return datetime.today() - time_to_subtract


def calc_fantasy_points(
    player_season: Dict[str, Any], stat_categories: Dict[str, float]
) -> int:
    total = 0
    for key, coeff in stat_categories.items():
        total = total + coeff * player_season[key]
    return total


def get_all_player_projections(
    player_projections: Dict[str, Dict[str, Any]],
    schedule_by_team: Dict[str, List[sqlite3.Row]],
):
    all_player_projections = []
    for player_projection in player_projections.values():
        team_id = player_projection["TEAM_ID"]
        games = schedule_by_team[team_id] if team_id in schedule_by_team.keys() else []
        all_player_projections.append(
            {
                "name": player_projection["PLAYER_NAME"],
                "age": player_projection["AGE"],
                "positions": "",
                "selected_position": "",
                "status": "",
                "fp_projection_preseason": player_projection["FP_PROJECTION_PRESEASON"],
                "fp_projection_current": player_projection["FP_PROJECTION_CURRENT"],
                "fp": player_projection["FP"],
                "fp_per_game": player_projection["FP"] / player_projection["GP"],
                "games_played": player_projection["GP"],
                "min": player_projection["MIN"],
                "min_per_game": player_projection["MIN"] / player_projection["GP"],
                "games": games,
            }
        )
    return all_player_projections


def get_fantasy_player_projections(
    fantasy_players: List[FantasyPlayer],
    player_projections: Dict[str, Dict[str, Any]],
    schedule_by_team: Dict[str, List[sqlite3.Row]],
):
    fantasy_player_projections = []
    for player in fantasy_players:
        name = remove_periods(player["name"])
        if name not in player_projections.keys():
            continue
        player_projection = player_projections[name]
        team_id = player_projection["TEAM_ID"]
        games = schedule_by_team[team_id] if team_id in schedule_by_team.keys() else []
        fantasy_player_projections.append(
            {
                **player,
                "age": player_projection["AGE"],
                "fp_projection_preseason": player_projection["FP_PROJECTION_PRESEASON"],
                "fp_projection_current": player_projection["FP_PROJECTION_CURRENT"],
                "fp": player_projection["FP"],
                "fp_per_game": player_projection["FP"] / player_projection["GP"],
                "games_played": player_projection["GP"],
                "min": player_projection["MIN"],
                "min_per_game": player_projection["MIN"] / player_projection["GP"],
                "games": games,
            }
        )
    return fantasy_player_projections


def print_fantasy_player_projections(
    fantasy_players: List[FantasyPlayerProjection],
    extra_weeks: int = 0,
    file_name: str = None,
):
    row_format = (
        "{:<4} {:<5} {:<25} {:<7} {:<24} {:<6} {:<12} {:<12} {:<10} {:<5} {:<7} {:<15}"
    )
    header = row_format.format(
        "Rk.",
        "Pos",
        "Player Name",
        "Status",
        "Positions",
        "Age",
        "FP/G (Pre)",
        "FP/G (Proj)",
        "FP/G",
        "GP",
        "MPG",
        "Schedule",
    )
    print(header)
    lines = [header]

    for index, player in enumerate(fantasy_players):
        game_days = get_days_string(player["games"], extra_weeks)
        row = row_format.format(
            index + 1,
            player["selected_position"],
            player["name"],
            player["status"],
            player["positions"],
            round(player["age"]),
            round(player["fp_projection_preseason"], 4),
            round(player["fp_projection_current"], 4),
            round(player["fp_per_game"], 4),
            player["games_played"],
            round(player["min_per_game"], 1),
            game_days,
        )
        print(row)
        lines.append(row)

    if file_name != None:
        write_txt("\n".join(lines), file_name)
