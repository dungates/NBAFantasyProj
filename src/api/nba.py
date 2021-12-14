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
