import json
import os
from constants import LEAGUE_TYPES, STAT_COEFFS


def calc_fantasy_points(player_season):
    total = 0
    for key, coeff in STAT_COEFFS.items():
        total = total + coeff * player_season[key]
    return total


def get_config_files():
    files = []
    for type_info in LEAGUE_TYPES.values():
        path = "config/" + type_info["key"]
        if not os.path.exists(path):
            continue
        with os.scandir(path) as entries:
            for file in entries:
                if file.is_file() and file.name.endswith(".json"):
                    files.append((type_info, file))
    return files


def option_selector(prompt, data, get_label):
    print(prompt)
    for index, item in enumerate(data):
        label = get_label(item)
        print(str(index + 1) + ". " + label)
    index = int(input("Enter a number: "))
    if index > 0 and index <= len(data):
        return data[index - 1]
    else:
        print("Invalid number\n")
        return option_selector(prompt, data, get_label)


def write_json(data, filename):
    with open("Data/" + filename + ".json", "w") as json_file:
        json.dump(data, json_file, indent=2)


def write_txt(data, filename):
    with open("Data/" + filename + ".txt", "w") as txt_file:
        txt_file.write(data)
