from datetime import datetime, timedelta
import json
import os
import pytz

from .constants import LEAGUE_TYPES


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


def get_start_of_week():
    today = datetime.now(tz=pytz.timezone("America/Los_Angeles")).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    first_day_of_week = today - timedelta(days=today.weekday())
    return first_day_of_week.isoformat()


def get_end_of_week():
    today = datetime.now(tz=pytz.timezone("America/Los_Angeles")).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    first_day_of_next_week = today + timedelta(days=7 - today.weekday())
    return first_day_of_next_week.isoformat()


def print_fantasy_players(players_list, file_name=None):
    row_format = "{:<4} {:<5} {:<25} {:<7} {:<20} {:<6} {:<12} {:<10} {:<5} {:<7} {:<5}"
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
    )
    print(header)
    lines = [header]

    for index, player in enumerate(players_list):
        selected_position = (
            player["selected_position"] if "selected_position" in player.keys() else ""
        )
        percent_owned = (
            player["percent_owned"] if "percent_owned" in player.keys() else ""
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
        )
        print(row)
        lines.append(row)

    if file_name != None:
        write_txt("\n".join(lines), file_name)
