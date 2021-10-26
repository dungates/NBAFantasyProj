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


if __name__ == "__main__":
    main()
