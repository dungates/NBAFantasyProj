import json
import os

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


def print_fantasy_players(players_list, file_name=None):
    row_format = "{:<4} {:<25} {:<7} {:<20} {:<6} {:<12} {:<10} {:<5} {:<7} {:<5}"
    header = row_format.format(
        "Rk.",
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
        row = row_format.format(
            str(index + 1),
            player["name"],
            player["status"],
            player["positions"],
            player["age"],
            player["preseason_fp_projection"],
            player["current_fp_projection"],
            player["games_played"],
            player["minutes_per_game"],
            player["percent_owned"],
        )
        print(row)
        lines.append(row)

    if file_name != None:
        write_txt("\n".join(lines), file_name)
