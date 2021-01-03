from nba_api.stats.endpoints import leaguedashplayerstats


def get_player_seasons(end_year, num_seasons):
    results = []
    for season in range(end_year - num_seasons, end_year):
        ending = str(season + 1)[-2:]
        full_season = str(season) + "-" + ending

        print("Retrieving data for " + str(season) + "...")
        stats = leaguedashplayerstats.LeagueDashPlayerStats(
            season=full_season, plus_minus="Y", rank="Y"
        )
        normalized_dict = stats.get_normalized_dict()["LeagueDashPlayerStats"]
        for player_season in normalized_dict:
            player_season["SEASON"] = season
            results.append(player_season)
    return results
