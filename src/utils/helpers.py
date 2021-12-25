from datetime import datetime, timedelta
import json
import os
import re
import sqlite3
from typing import Dict, List
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


def get_config_files():
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


def option_selector(prompt, data, get_label=None):
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


def write_json(data, filename):
    with open(f"Data/{filename}.json", "w") as json_file:
        json.dump(data, json_file, indent=2)


def write_txt(data, filename):
    with open(f"Data/{filename}.txt", "w") as txt_file:
        txt_file.write(data)


def remove_periods(str):
    return str.replace(".", "")


def get_current_season():
    today = datetime.today()
    return today.year if today.month < 9 else today.year + 1


def format_season(season):
    return str(season - 1) + "-" + str(season)[-2:]


def get_current_season_full():
    current_season = get_current_season()
    return format_season(current_season)


def get_current_time():
    return datetime.now(tz=pytz.timezone("America/Los_Angeles"))


def iso_8601_to_unix(iso):
    formatted_iso = re.sub(r"Z$", "+00:00", iso)
    return datetime.fromisoformat(formatted_iso).timestamp()


def get_start_of_week(weeks_from_now=0):
    today = get_current_time()
    first_day_of_week = (
        today + timedelta(weeks=weeks_from_now) - timedelta(days=today.weekday())
    )
    return first_day_of_week.replace(
        hour=0, minute=0, second=0, microsecond=0
    ).timestamp()


def get_end_of_week(weeks_from_now=0):
    today = get_current_time()
    first_day_of_next_week = (
        today + timedelta(weeks=weeks_from_now) + timedelta(days=7 - today.weekday())
    )
    return first_day_of_next_week.replace(
        hour=0, minute=0, second=0, microsecond=0
    ).timestamp()


def print_fantasy_players(
    players_list, schedule_by_team, extra_weeks=0, file_name=None
):
    days_schedule_by_team = get_days_schedule_by_team(schedule_by_team, extra_weeks)

    row_format = (
        "{:<4} {:<5} {:<25} {:<7} {:<24} {:<6} {:<12} {:<10} {:<5} {:<7} {:<8} {:<15}"
    )
    header = row_format.format(
        "Rk.",
        "Pos",
        "Player Name",
        "Status",
        "Positions",
        "Age",
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
        team_id = player["team_id"]
        selected_position = (
            player["selected_position"] if "selected_position" in player.keys() else ""
        )
        percent_owned = (
            player["percent_owned"] if "percent_owned" in player.keys() else ""
        )
        game_days = (
            days_schedule_by_team[team_id]
            if team_id in days_schedule_by_team.keys()
            else ""
        )
        row = row_format.format(
            str(index + 1),
            selected_position,
            player["name"],
            player["status"],
            player["positions"],
            round(player["age"]),
            round(player["preseason_fp_projection"], 4),
            round(player["current_fp_projection"], 4),
            player["games_played"],
            round(player["minutes_per_game"], 2),
            percent_owned,
            game_days,
        )
        print(row)
        lines.append(row)

    if file_name != None:
        write_txt("\n".join(lines), file_name)
