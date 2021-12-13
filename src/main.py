from datetime import datetime
import os
from sys import platform
from api.database import get_player_projections, get_schedule_by_team
from api.yahoo import YahooClient
from utils.constants import LEAGUE_TYPES, YAHOO_STAT_COEFFS
from utils.helpers import (
    get_config_files,
    get_end_of_week,
    get_start_of_week,
    option_selector,
    write_json,
)


def iso_to_timestamp(iso):
    return datetime.fromisoformat(iso).timestamp()


# def filter_games_from_range(season_games, start_time, end_time):
#     weekly_games = []
#     for game in season_games:
#         start_time = iso_to_timestamp(start_time)
#         end_time = iso_to_timestamp(end_time)
#         game_time = iso_to_timestamp(game["gameDateTimeUTC"])
#         if start_time < game_time and game_time < end_time:
#             weekly_games.append(game)
#     return weekly_games


# def get_weekly_schedule_by_team(schedule_by_team):
#     weekly_schedule = {}
#     for team_id, games in enumerate(schedule_by_team):
#         start_time = get_start_of_week()
#         end_time = get_end_of_week()
#         weekly_schedule[team_id] = len(
#             filter_games_from_range(games, start_time, end_time)
#         )
#     return weekly_schedule


def add_fantasy_account():
    selected_option = option_selector(
        "Add a fantasy sports account...",
        list(LEAGUE_TYPES.values()),
        lambda league_type: league_type["name"],
    )
    selected_key = selected_option[1]["key"]

    name = input("Enter account name: ")
    config_file_dir = f"config/{selected_key}"
    config_file_name = f"{config_file_dir}/{name}.json"
    if os.path.exists(config_file_name):
        print(f"Account with name '{name}' already exists!")
        return

    os.makedirs(config_file_dir, exist_ok=True)

    with os.scandir(config_file_dir) as entries:
        for file in entries:
            if file.is_file() and file.name.endswith(".json"):
                print(file.name)

    if selected_key == "yahoo":
        key = input("Enter consumer key: ")
        secret = input("Enter consumer secret: ")
        command = (
            f"python {os.getenv('VIRTUAL_ENV')}/env/Scripts/yfa_init_oauth_env"
            if platform == "win32"
            else "yfa_init_oauth_env"
        )
        args = f"-k {key} -s {secret} {config_file_dir}/{name}.json"
        os.system(f"{command} {args}")
    elif selected_key == "espn":
        espn_s2 = input("Enter espn_s2 variable: ")
        swid = input("Enter swid variable: ")
        json_object = {"espn_s2": espn_s2, "swid": swid}
        write_json(json_object, f"{config_file_dir}/{name}.json")

    main()


def load_fantasy_account():
    config_files = get_config_files()
    league_info = option_selector(
        "Select existing fantasy sports account...",
        config_files,
        lambda file_data: f"[{file_data[0]['name']}] {file_data[1].name}",
    )
    selected_key = league_info[1][0]["key"]

    if selected_key == "yahoo":
        yahoo_client = YahooClient(league_info[1][1].path)
        current_league = yahoo_client.get_current_league()

        print("\nFetching player projections..")
        player_projections = get_player_projections(YAHOO_STAT_COEFFS)

        print("\nFetching upcoming game schedule...")
        # schedule_by_team = get_schedule_by_team()
        # weekly_schedules = get_weekly_schedule_by_team(schedule_by_team)

        print("\nFetching free agents...")
        yahoo_client.fetch_free_agents(current_league, player_projections)

        print("\nFetching fantasy matchups for current week...")
        current_matchups = yahoo_client.get_matchups(current_league)
        for team1, team2 in current_matchups:
            print(
                f"\n{team1['name']} ({team1['points_total']}) vs. {team2['name']} ({team2['points_total']})"
            )
            yahoo_client.print_roster(team1, player_projections)
            yahoo_client.print_roster(team2, player_projections)
            print("\n")


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
            load_fantasy_account()
    else:
        print("No config files found!")
        add_fantasy_account()


if __name__ == "__main__":
    main()
