from dateutil import parser
from dateutil.tz import gettz
from pyquery import PyQuery as pq
import requests
import tabula


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


def fetch_injury_report_page() -> pq | None:
    print("Fetching current injury report...")
    try:
        response = requests.get(
            "https://official.nba.com/nba-injury-report-2021-22-season/"
        )
        return pq(response.text)
    except requests.ConnectionError:
        print("Unable to fetch injury report data")
        return None


def fetch_current_injury_report():
    d = fetch_injury_report_page()
    date = d(".entry-content b")[0].text.replace(":", "")
    links = d(".entry-content a")
    for link in links:
        time_data = link.text.replace(".", "").replace(" report", "")
        tzinfos = {"ET": gettz("America/New_York")}
        update_time = parser.parse(f"{date}, {time_data}", tzinfos=tzinfos)
        try:
            tabula.convert_into(
                link.attrib["href"],
                f"Data/{update_time.timestamp()}.csv",
                output_format="csv",
                pages="all",
            )
        except requests.ConnectionError:
            print("Unable to fetch injury data")
