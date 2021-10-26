import json
from constants import STAT_COEFFS


def calc_fantasy_points(player_season):
    total = 0
    for key, coeff in STAT_COEFFS.items():
        total = total + coeff * player_season[key]
    return total


def option_selector(prompt, options):
    print(prompt)
    for index, option in enumerate(options):
        print(str(index + 1) + ". " + option["label"])
    index = int(input("Enter a number: "))
    if index > 0 and index <= len(options):
        return options[index - 1]["data"]
    else:
        print("Invalid number\n")
        return option_selector(prompt, options)


def write_json(data, filename):
    with open("Data/" + filename + ".json", "w") as json_file:
        json.dump(data, json_file, indent=2)


def write_txt(data, filename):
    with open("Data/" + filename + ".txt", "w") as txt_file:
        txt_file.write(data)
