import json
from nba_api.stats.library.parameters import Season, SeasonYear, SeasonID
from constants import SEASON_WEIGHTS
from utils import get_weighted_average, inject_fantasy_points


num_past_seasons = len(SEASON_WEIGHTS)


def get_player_stats(name):
    with open("Data/seasonTotalsByPlayer.json") as json_file:
        data = json.load(json_file)
        for player_season_list in data.values():
            if player_season_list[0]["PLAYER_NAME"].lower() == name.lower():
                return player_season_list
    return None


# TODO: REFACTOR THIS FUCKING MESS!!!!
def main():
    player_name = input("Player Name: ")
    player_season_list = get_player_stats(player_name)
    if not player_season_list:
        print("Player not found!")
        return

    inject_fantasy_points(player_season_list)

    num_seasons = len(player_season_list)
    print("Number of seasons: " + str(num_seasons))

    past_seasons = player_season_list[-num_past_seasons:]
    past_seasons.reverse()
    print("Number of past seasons: " + str(len(past_seasons)))

    print("Age" + "\t" + "FP/G" + "\t" + "GP")
    for player_season in player_season_list:
        fantasy_ppg = player_season["FP"] / player_season["GP"]
        print(
            str(player_season["AGE"])
            + "\t"
            + str(round(fantasy_ppg, 4))
            + "\t"
            + str(player_season["GP"])
        )

    weighted_average = get_weighted_average(past_seasons)
    print(
        "Weighted average FP/G over past "
        + str(num_past_seasons)
        + " seasons: "
        + str(weighted_average)
    )


if __name__ == "__main__":
    main()
