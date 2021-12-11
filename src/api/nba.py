from datetime import datetime
import requests


def fetch_current_schedule():
    print("Fetching game schedule for current season...")
    try:
        response = requests.get(
            "https://cdn.nba.com/static/json/staticData/scheduleLeagueV2.json"
        )
        data = response.json()
        return data
    except requests.ConnectionError:
        print("Unable to fetch schedule data")
        return None


def get_current_season():
    today = datetime.today()
    return today.year if today.month < 9 else today.year + 1


def format_season(season):
    return str(season - 1) + "-" + str(season)[-2:]


def get_current_season_full():
    current_season = get_current_season()
    return format_season(current_season)
