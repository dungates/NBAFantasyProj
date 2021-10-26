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
        path = "config/{}".format(type_info["key"])
        if not os.path.exists(path):
            continue
        with os.scandir(path) as entries:
            for file in entries:
                if file.is_file() and file.name.endswith(".json"):
                    files.append((type_info, file))
    return files


def option_selector(prompt, data, get_label=None):
    print("\n{}".format(prompt))
    for index, item in enumerate(data):
        label = str(item) if get_label == None else get_label(item)
        print("{}. {}".format(str(index + 1), label))
    index = int(input("Enter a number: ")) - 1
    if index >= 0 and index < len(data):
        return (index, data[index])
    else:
        print("Invalid number")
        return option_selector(prompt, data, get_label)


def write_json(data, filename):
    with open("Data/{}.json".format(filename), "w") as json_file:
        json.dump(data, json_file, indent=2)


def write_txt(data, filename):
    with open("Data/{}.txt".format(filename), "w") as txt_file:
        txt_file.write(data)
