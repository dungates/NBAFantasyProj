from api.database import (
    update_current_schedule,
    update_last_totals,
    update_player_season,
)
from utils.helpers import get_current_season


def update_current_season_stats():
    current_season = get_current_season()
    update_player_season(current_season)
    update_last_totals("month")
    update_last_totals("week")


if __name__ == "__main__":
    update_current_schedule()
    update_current_season_stats()
