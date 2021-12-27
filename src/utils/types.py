import sqlite3
from typing import List, TypedDict


class FantasyPlayer(TypedDict):
    name: str
    status: str
    positions: str
    selected_position: str


class FantasyPlayerProjection(FantasyPlayer):
    age: float
    fp_projection_preseason: float
    fp_projection_current: float
    fp: float
    fp_per_game: float
    games_played: int
    min: float
    min_per_game: float
    games: List[sqlite3.Row]
