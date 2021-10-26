import os
from constants import LEAGUE_TYPES
from utils import option_selector


def main():
    options = []
    for key, info in LEAGUE_TYPES.items():
        with os.scandir("config/" + key) as entries:
            for entry in entries:
                if ".json" in entry.name:
                    options.append(
                        {
                            "label": "["
                            + info["name"]
                            + "] "
                            + entry.name.replace(".json", ""),
                            "data": {
                                "type": key,
                                "config_path": entry.path,
                            },
                        }
                    )
    league_info = option_selector("Please select a league...", options)
    print(league_info)


if __name__ == "__main__":
    main()
