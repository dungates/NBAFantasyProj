from nba_api.stats.endpoints import leaguedashplayerstats, leaguegamelog
from api.nba import get_current_season_full
from pydash.collections import order_by
from constants import (
    CURRENT_SEASON_NUM_GAMES,
    CURRENT_SEASON_NUM_TEAMS,
    MIN_REQUIREMENT_NORMAL_SEASON,
)
from utils import write_json


def get_min_requirement():
    full_season = get_current_season_full()
    stats = leaguegamelog.LeagueGameLog(season=full_season)
    stats_totals = stats.get_normalized_dict()["LeagueGameLog"]

    total_min_requirement = (
        MIN_REQUIREMENT_NORMAL_SEASON * CURRENT_SEASON_NUM_GAMES / 82
    )

    num_games_total = CURRENT_SEASON_NUM_GAMES * CURRENT_SEASON_NUM_TEAMS
    num_games_played = len(stats_totals)
    pct_games_played = num_games_played / num_games_total

    return pct_games_played * total_min_requirement


def inject_scoring_rating(player_season, player_season_per_100):
    true_shooting_att = player_season["FGA"] + 0.44 * player_season["FTA"]
    effective_fgm = player_season["FGM"] + 0.5 * player_season["FG3M"]

    player_season["TSA"] = true_shooting_att
    if true_shooting_att * player_season["FGA"] == 0:
        return

    true_shooting_pct = player_season["PTS"] / (2 * true_shooting_att)
    effective_fg_pct = effective_fgm / player_season["FGA"]

    efficiency_sum = true_shooting_pct + effective_fg_pct

    points_per_game = player_season["PTS"] / player_season["GP"]
    ftm_per_game = player_season["FTM"] / player_season["GP"]

    scoring_rating = efficiency_sum * (
        points_per_game
        + player_season_per_100["PTS"]
        - (ftm_per_game + player_season_per_100["FTM"]) / 2
    )
    player_season["SCORING_RATING"] = scoring_rating


def print_stats(player_seasons_by_scoring_rtg):
    min_requirement = get_min_requirement()
    rank = 1
    print(
        "Rk. Player Name\t\tTeam\t\tScoring Rating\t\tGP\tMPG\tPPG\tFG%/3P%/FT%\tTSA/G"
    )
    for player_season in player_seasons_by_scoring_rtg:
        if player_season["MIN"] < min_requirement:
            continue
        print(
            str(rank)
            + ". "
            + player_season["PLAYER_NAME"]
            + "\t\t"
            + player_season["TEAM_ABBREVIATION"]
            + "\t\t"
            + str(round(player_season["SCORING_RATING"], 8))
            + "\t\t"
            + str(player_season["GP"])
            + "\t"
            + str(round(player_season["MIN"] / player_season["GP"], 1))
            + "\t"
            + str(round(player_season["PTS"] / player_season["GP"], 1))
            + "\t"
            + str(round(100 * player_season["FG_PCT"], 1))
            + "/"
            + str(round(100 * player_season["FG3_PCT"], 1))
            + "/"
            + str(round(100 * player_season["FT_PCT"], 1))
            + "\t"
            + str(round(player_season["TSA"] / player_season["GP"], 1))
        )
        rank = rank + 1


def main():
    full_season = get_current_season_full()

    stats = leaguedashplayerstats.LeagueDashPlayerStats(season=full_season)
    stats_totals = stats.get_normalized_dict()["LeagueDashPlayerStats"]

    write_json(stats_totals, "statsTotalsSeason")

    stats = leaguedashplayerstats.LeagueDashPlayerStats(
        season=full_season, per_mode_detailed="Per100Possessions"
    )
    stats_per_100 = stats.get_normalized_dict()["LeagueDashPlayerStats"]

    for player_season, player_season_per_100 in zip(stats_totals, stats_per_100):
        inject_scoring_rating(player_season, player_season_per_100)

    player_seasons_by_tsa = order_by(stats_totals, ["-TSA"])
    for index, player_season in enumerate(player_seasons_by_tsa):
        player_season["TSA_RANK"] = index + 1

    player_seasons_by_scoring_rtg = order_by(player_seasons_by_tsa, ["-SCORING_RATING"])

    print_stats(player_seasons_by_scoring_rtg)


if __name__ == "__main__":
    main()