from constants import LEAGUE_TYPES
from utils import get_config_files, option_selector


def main():
    config_files = get_config_files()
    if len(config_files):
        league_info = option_selector(
            "Please select a league...",
            config_files,
            lambda file_data: "[" + file_data[0]["name"] + "] " + file_data[1].name,
        )
        print(league_info)
    else:
        print("No config files found!")
        selected_option = option_selector(
            "Add a fantasy sports account...",
            list(LEAGUE_TYPES.values()),
            lambda league_type: league_type["name"],
        )
        print(selected_option)


if __name__ == "__main__":
    main()
