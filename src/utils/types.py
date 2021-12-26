from typing import TypedDict


class FantasyPlayer(TypedDict):
    name: str
    status: str
    positions: str
    selected_position: str
    percent_owned: int
