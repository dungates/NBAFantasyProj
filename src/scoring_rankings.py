from nba_api.stats.endpoints import leaguedashplayerstats, leaguegamelog
from pydash.collections import order_by
from api.nba import get_current_season_full
from utils.constants import (
    CURRENT_SEASON_NUM_GAMES,
    CURRENT_SEASON_NUM_TEAMS,
    TSA_REQUIREMENT_NORMAL_SEASON,
)
from utils.helpers import write_txt


def get_tsa_requirement():
    # Get current NBA season
    full_season = get_current_season_full()

    # Fetch league game log for current season
    stats = leaguegamelog.LeagueGameLog(season=full_season)
    current_gamelog = stats.get_normalized_dict()["LeagueGameLog"]

    # Calculate true shooting attempts (TSA) qualifier for current season
    # TSA = FGA + 0.44 * FTA
    total_tsa_requirement = (
        TSA_REQUIREMENT_NORMAL_SEASON / 82 * CURRENT_SEASON_NUM_GAMES
    )

    # Calculate percentage of total scheduled NBA games played so far
    num_games_played = len(current_gamelog)
    num_games_total = CURRENT_SEASON_NUM_GAMES * CURRENT_SEASON_NUM_TEAMS
    pct_games_played = num_games_played / num_games_total

    return pct_games_played * total_tsa_requirement


def inject_scoring_rating(player_season_totals, player_season_per_100):
    # Calculate TSA and eFGM
    true_shooting_att = player_season_totals["FGA"] + 0.44 * player_season_totals["FTA"]
    effective_fgm = player_season_totals["FGM"] + 0.5 * player_season_totals["FG3M"]

    # Avoid divide by zero error
    player_season_totals["TSA"] = true_shooting_att
    if true_shooting_att * player_season_totals["FGA"] == 0:
        return

    # Calculate TS% and eFG%
    # TS% = PTS / (2 * TSA)
    # eFG% = eFGM / FGA
    true_shooting_pct = player_season_totals["PTS"] / (2 * true_shooting_att)
    effective_fg_pct = effective_fgm / player_season_totals["FGA"]

    # Sum TS% and eFG% to get overall efficiency
    efficiency_sum = true_shooting_pct + effective_fg_pct

    # Calculate PTS/G and FTM/G
    pts_per_game = player_season_totals["PTS"] / player_season_totals["GP"]
    ftm_per_game = player_season_totals["FTM"] / player_season_totals["GP"]

    # Calculate scoring rating
    scoring_rating = efficiency_sum * (
        pts_per_game
        + player_season_per_100["PTS"]
        - (ftm_per_game + player_season_per_100["FTM"]) / 2
    )

    # Set scoring rating
    player_season_totals["SCORING_RATING"] = scoring_rating


def print_stats(player_seasons_by_scoring_rtg):
    # Get TSA qualifier
    tsa_requirement = get_tsa_requirement()

    # Initialize rank counter
    rank = 1

    # Define row format and print header
    row_format = "{:<5} {:<25} {:<10} {:<15} {:<5} {:<5} {:<5} {:<20} {:<5}"
    header = row_format.format(
        "Rk.",
        "Player Name",
        "Team",
        "Scoring Rtg",
        "GP",
        "MPG",
        "PPG",
        "FG%/3P%/FT%",
        "TSA/G",
    )

    # Print header and initialize lines array
    print(header)
    lines = [header]

    # Iterate over list of player stats
    for player_season in player_seasons_by_scoring_rtg:
        # Skip player if not qualified
        if player_season["TSA"] < tsa_requirement:
            continue

        # Format shooting splits string
        shooting_splits = "/".join(
            [
                str(round(100 * player_season["FG_PCT"], 1)),
                str(round(100 * player_season["FG3_PCT"], 1)),
                str(round(100 * player_season["FT_PCT"], 1)),
            ]
        )

        # Format data row
        row = row_format.format(
            rank,
            player_season["PLAYER_NAME"],
            player_season["TEAM_ABBREVIATION"],
            round(player_season["SCORING_RATING"], 8),
            player_season["GP"],
            round(player_season["MIN"] / player_season["GP"], 1),
            round(player_season["PTS"] / player_season["GP"], 1),
            shooting_splits,
            round(player_season["TSA"] / player_season["GP"], 1),
        )

        # Print row and add to lines array
        print(row)
        lines.append(row)

        # Increment rank
        rank = rank + 1

    # Write lines to file
    write_txt("\n".join(lines), "scoring_stats")


def main():
    # Get current NBA season
    full_season = get_current_season_full()

    # Fetch current season stats (totals and per 100)
    stats = leaguedashplayerstats.LeagueDashPlayerStats(season=full_season)
    stats_totals = stats.get_normalized_dict()["LeagueDashPlayerStats"]

    stats = leaguedashplayerstats.LeagueDashPlayerStats(
        season=full_season, per_mode_detailed="Per100Possessions"
    )
    stats_per_100 = stats.get_normalized_dict()["LeagueDashPlayerStats"]

    # Calculate scoring rating for each player
    for player_season_totals, player_season_per_100 in zip(stats_totals, stats_per_100):
        inject_scoring_rating(player_season_totals, player_season_per_100)

    # Sort players by scoring rating
    player_seasons_by_scoring_rtg = order_by(stats_totals, ["-SCORING_RATING"])

    # Output data
    print_stats(player_seasons_by_scoring_rtg)


if __name__ == "__main__":
    main()
