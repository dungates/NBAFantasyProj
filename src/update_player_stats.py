import json
from pydash.collections import group_by, order_by
from api.nba import get_player_seasons
from api.yahoo import get_current_season
from utils import write_json


if __name__ == "__main__":
    current_season = get_current_season()
    results = get_player_seasons(current_season, 20)
    grouped_data = group_by(results, "PLAYER_ID")
    for value in grouped_data.values():
        order_by(value, "AGE")
    write_json(grouped_data, "seasonTotalsByPlayer")
