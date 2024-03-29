from api.database import (
    update_current_schedule,
    update_player_last_totals,
    update_opponent_last_totals,
    update_opponent_season_totals,
    update_player_season,
    update_team_last_totals,
    update_team_season_totals,
)
from utils.helpers import get_current_season


def update_current_player_stats():
    current_season = get_current_season()
    update_player_season(current_season)
    update_player_last_totals("month")
    update_player_last_totals("week")


def update_current_team_stats():
    current_season = get_current_season()
    update_team_season_totals(current_season)
    update_team_last_totals("month")
    update_team_last_totals("week")


def update_current_opponent_stats():
    current_season = get_current_season()
    update_opponent_season_totals(current_season)
    update_opponent_last_totals("month")
    update_opponent_last_totals("week")


def main():
    update_current_schedule()
    update_current_player_stats()
    update_current_team_stats()
    update_current_opponent_stats()


if __name__ == "__main__":
    main()
