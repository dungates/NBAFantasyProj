import os
from sys import platform
from pydash.collections import order_by
from api.database import get_schedule_by_team
from api.sleeper import SleeperClient
from api.yahoo import YahooClient
from utils.constants import LEAGUE_TYPES, YAHOO_STAT_COEFFS
from utils.helpers import (
    get_all_player_projections,
    print_fantasy_player_projections,
)
from utils.player_projection import get_fantasy_projections


def main():
    player_projections = get_fantasy_projections(YAHOO_STAT_COEFFS)
    schedule_by_team = get_schedule_by_team()

    all_projections = get_all_player_projections(player_projections, schedule_by_team)
    ordered_projections = order_by(all_projections, ["-fp_projection_current"])

    print(f"\nTop players")
    print_fantasy_player_projections(
        ordered_projections,
        1,
        file_name="all_projections",
    )


if __name__ == "__main__":
    main()
