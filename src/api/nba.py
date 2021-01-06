from datetime import datetime
from nba_api.stats.endpoints import leaguedashplayerstats


def get_current_season():
    today = datetime.today()
    return today.year if today.month < 9 else today.year + 1


def get_current_season_full():
    current_season = get_current_season()
    return str(current_season - 1) + "-" + str(current_season)[-2:]


def get_player_season_stats(end_season, num_seasons):
    results = []
    for season in range(end_season + 1 - num_seasons, end_season + 1):
        full_season = str(season - 1) + "-" + str(season)[-2:]

        print("Retrieving player stats for " + full_season + "...")
        stats = leaguedashplayerstats.LeagueDashPlayerStats(season=full_season)
        normalized_stats = stats.get_normalized_dict()["LeagueDashPlayerStats"]
        for player_season in normalized_stats:
            new_season = {}
            for key, value in player_season.items():
                if "_RANK" not in key:
                    new_season[key] = value
            new_season["SEASON"] = season
            results.append(new_season)
    return results
