import json
from nba_api.stats.endpoints import leaguedashplayerstats
from pydash.collections import group_by, order_by


results = []
for i in range(1, 11):
    ending = "0" + str(i) if i < 10 else str(i)
    season = str(2000 + i - 1) + "-" + ending

    print("Retrieving data for " + season + "...")
    stats = leaguedashplayerstats.LeagueDashPlayerStats(
        season=season,
    )
    normalized_dict = stats.get_normalized_dict()
    results += normalized_dict["LeagueDashPlayerStats"]


grouped_data = group_by(results, "PLAYER_ID")

for value in grouped_data.values():
    order_by(value, "AGE")

with open("result.json", "w") as fp:
    json.dump(grouped_data, fp)
