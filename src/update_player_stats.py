import json
from pydash.collections import group_by, order_by
from api.nba import get_player_seasons
from api.yahoo import get_current_season
from utils import write_json


if __name__ == "__main__":
    # Get current NBA season
    current_season = get_current_season()

    # Fetch player season data for last 20 seasons
    results = get_player_seasons(current_season - 1, 20)

    # Order results by player age
    order_by(results, "AGE")

    # Group data by player
    grouped_data = group_by(results, "PLAYER_ID")

    # Write data to JSON file
    write_json(grouped_data, "seasonTotalsByPlayer")
