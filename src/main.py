from constants import LEAGUE_TYPES
from utils import get_config_files, option_selector


def add_fantasy_account():
    selected_option = option_selector(
        "Add a fantasy sports account...",
        list(LEAGUE_TYPES.values()),
        lambda league_type: league_type["name"],
    )
    print(selected_option)


def load_fantasy_account():
    config_files = get_config_files()
    league_info = option_selector(
        "Select existing fantasy sports account...",
        config_files,
        lambda file_data: "[{}] {}".format(file_data[0]["name"], file_data[1].name),
    )
    return league_info[1]


def main():
    config_files = get_config_files()
    if len(config_files):
        choice = option_selector(
            "Please select an option...",
            [
                "Add a fantasy sports account",
                "Select existing fantasy sports account",
            ],
        )
        if choice[0] == 0:
            add_fantasy_account()
        elif choice[0] == 1:
            account_info = load_fantasy_account()
            print(account_info)
    else:
        print("No config files found!")
        add_fantasy_account()


if __name__ == "__main__":
    main()
