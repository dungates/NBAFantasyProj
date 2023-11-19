LEAGUE_TYPES = {
    "yahoo": {"key": "yahoo", "name": "Yahoo"},
    "espn": {"key": "espn", "name": "ESPN"},
    "sleeper": {"key": "sleeper", "name": "Sleeper"},
}

YAHOO_STAT_COEFFS = {
    "FG3M": 1,
    "PTS": 1,
    "REB": 1.2,
    "AST": 1.5,
    "STL": 3,
    "BLK": 3,
    "TOV": -1,
}

ESPN_STAT_COEFFS = {
    "FGM": 2,
    "FGA": -1,
    "FTM": 1,
    "FTA": -1,
    "FG3M": 1,
    "PTS": 1,
    "REB": 1,
    "AST": 2,
    "STL": 4,
    "BLK": 4,
    "TOV": -2,
}

DAYS_OF_WEEK = {
    "Mon": "M",
    "Tue": "T",
    "Wed": "W",
    "Thu": "R",
    "Fri": "F",
    "Sat": "S",
    "Sun": "U",
}

PEAK_AGE = 28

CURRENT_SEASON_NUM_GAMES = 82
CURRENT_SEASON_NUM_TEAMS = 30
TSA_REQUIREMENT_NORMAL_SEASON = 200
