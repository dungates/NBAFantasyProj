from datetime import datetime, timedelta
from nba_api.stats.endpoints import leaguedashplayerstats


def get_current_season():
    today = datetime.today()
    return today.year if today.month < 9 else today.year + 1


def format_season(season):
    return str(season - 1) + "-" + str(season)[-2:]


def get_current_season_full():
    current_season = get_current_season()
    return format_season(current_season)


def parse_player_stats(player_stats):
    normalized_player_stats = player_stats.get_normalized_dict()[
        "LeagueDashPlayerStats"
    ]
    results = {}
    for player_season in normalized_player_stats:
        new_player_season = {}
        for key, value in player_season.items():
            if "_RANK" not in key:
                new_player_season[key] = value
        results[player_season["PLAYER_ID"]] = new_player_season
    return results


def get_season_stats(season):
    full_season = format_season(season)
    stats = leaguedashplayerstats.LeagueDashPlayerStats(season=full_season)
    return parse_player_stats(stats)


def get_current_season_stats(last_range):
    current_season = get_current_season_full()
    time_to_subtract = None
    if last_range == "week":
        time_to_subtract = timedelta(days=7)
    elif last_range == "month":
        time_to_subtract = timedelta(days=30.4375)

    if not time_to_subtract:
        stats = leaguedashplayerstats.LeagueDashPlayerStats(season=current_season)
        return parse_player_stats(stats)

    date_from = datetime.today() - time_to_subtract
    stats = leaguedashplayerstats.LeagueDashPlayerStats(
        season=current_season, date_from_nullable=date_from
    )
    return parse_player_stats(stats)
