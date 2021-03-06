from pydash.collections import group_by
from api.nba import get_current_season, get_past_season_stats
from utils import write_json


if __name__ == "__main__":
    # Get current NBA season
    current_season = get_current_season()

    # Fetch player season data for last 20 seasons
    results = get_past_season_stats(current_season - 1, 20)

    # Group data by player
    grouped_data = group_by(results, "PLAYER_ID")

    # Write data to JSON file
    write_json(grouped_data, "seasonTotalsByPlayer")
