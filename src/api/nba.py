from nba_api.stats.endpoints import leaguedashplayerstats


def get_player_seasons(end_season, num_seasons):
    results = []
    for season in range(end_season + 1 - num_seasons, end_season + 1):
        full_season = str(season - 1) + "-" + str(season)[-2:]

        print("Retrieving data for " + full_season + "...")
        stats = leaguedashplayerstats.LeagueDashPlayerStats(
            season=full_season, plus_minus="Y", rank="Y"
        )
        normalized_dict = stats.get_normalized_dict()["LeagueDashPlayerStats"]
        for player_season in normalized_dict:
            player_season["SEASON"] = season
            results.append(player_season)
    return results
