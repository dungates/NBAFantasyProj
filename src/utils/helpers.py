from datetime import datetime, timedelta
import json
import os
import re
import sqlite3
from types import FunctionType
from typing import Any, Dict, List, Tuple
import pytz

from .constants import DAYS_OF_WEEK, LEAGUE_TYPES


def get_weekly_days_string(
    team_games: List[sqlite3.Row], weeks_from_now: int = 0
) -> List[str]:
    start_time = get_start_of_week(weeks_from_now)
    end_time = get_end_of_week(weeks_from_now)
    game_days = []
    for game in team_games:
        game_time = iso_8601_to_unix(game["gameDateTimeUTC"])
        if start_time < game_time and game_time < end_time:
            game_days.append(game["day"])
    days = ""
    for day in DAYS_OF_WEEK.keys():
        char = DAYS_OF_WEEK[day] if day in game_days else " "
        days += char
    return days


def get_days_schedule_by_team(
    schedule_by_team: Dict[str, List[sqlite3.Row]], extra_weeks: int = 0
) -> Dict[str, str]:
    weekly_schedule = {}
    for weeks_from_now in range(0, extra_weeks + 1):
        for team_id, games in schedule_by_team.items():
            if team_id not in weekly_schedule.keys():
                weekly_schedule[team_id] = ""
            weekly_game_days = get_weekly_days_string(games, weeks_from_now)
            if weeks_from_now > 0:
                weekly_schedule[team_id] += "  "
            weekly_schedule[team_id] += weekly_game_days
    return weekly_schedule


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
    with open(f"Data/{filename}.json", "w") as json_file:
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


def calc_fantasy_points(
    player_season: Dict[str, Any], stat_categories: Dict[str, float]
) -> int:
    total = 0
    for key, coeff in stat_categories.items():
        total = total + coeff * player_season[key]
    return total


def print_fantasy_players(
    players_list: List[Dict[str, Any]],
    player_projections: Dict[str, Dict[str, Any]],
    schedule_by_team: Dict[str, List[sqlite3.Row]],
    extra_weeks: int = 0,
    file_name: str = None,
):
    days_schedule_by_team = get_days_schedule_by_team(schedule_by_team, extra_weeks)

    row_format = "{:<4} {:<5} {:<25} {:<7} {:<24} {:<6} {:<12} {:<12} {:<10} {:<5} {:<7} {:<8} {:<15}"
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
        "% Owned",
        "Schedule",
    )
    print(header)
    lines = [header]

    for index, player in enumerate(players_list):
        name = remove_periods(player["name"])
        if name not in player_projections.keys():
            continue
        player_projection = player_projections[name]
        team_id = player_projection["TEAM_ID"]
        game_days = (
            days_schedule_by_team[team_id]
            if team_id in days_schedule_by_team.keys()
            else ""
        )
        row = row_format.format(
            str(index + 1),
            player["selected_position"],
            player["name"],
            player["status"],
            player["positions"],
            round(player_projection["AGE"]),
            round(player_projection["FP_PROJECTION_PRESEASON"], 4),
            round(player_projection["FP_PROJECTION_CURRENT"], 4),
            round(player_projection["FP"] / player_projection["GP"], 4),
            player_projection["GP"],
            round(player_projection["MIN"] / player_projection["GP"], 2),
            player["percent_owned"],
            game_days,
        )
        print(row)
        lines.append(row)

    if file_name != None:
        write_txt("\n".join(lines), file_name)
