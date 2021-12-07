from nba_api.stats.endpoints import leaguedashplayerstats
from pydash.objects import get

from utils.sqlite import update_data_table


def update_season_stats(season):
    stats_response = leaguedashplayerstats.LeagueDashPlayerStats(season=season)

    data = get(stats_response, "data_sets.0.data")
    headers = get(data, "headers")
    data_rows = get(data, "data")
    if not len(data_rows):
        return

    primary_keys = ["SEASON", "PLAYER_NAME"]
    extra_values = [("SEASON", season)]
    update_data_table("test_table", headers, data_rows, primary_keys, extra_values)


if __name__ == "__main__":
    update_season_stats("2021-22")
