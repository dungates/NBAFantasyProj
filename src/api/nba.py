from datetime import datetime, timedelta
from nba_api.stats.endpoints import leaguedashplayerstats
from pydash.collections import key_by
from utils.constants import PEAK_AGE

from utils.player_projection import calc_player_projection


class NBAClient:
    def get_current_season(self):
        today = datetime.today()
        return today.year if today.month < 9 else today.year + 1

    def format_season(self, season):
        return str(season - 1) + "-" + str(season)[-2:]

    def get_current_season_full(self):
        current_season = self.get_current_season()
        return self.format_season(current_season)

    def parse_player_stats(self, player_stats):
        normalized_player_stats = player_stats.get_normalized_dict()[
            "LeagueDashPlayerStats"
        ]
        results = {}
        for player_season in normalized_player_stats:
            new_player_season = {}
            for key, value in player_season.items():
                if "_RANK" not in key:
                    new_player_season[key] = value
            results[player_season["PLAYER_ID"]] = new_player_season
        return results

    def get_season_stats(self, season):
        full_season = self.format_season(season)
        stats = leaguedashplayerstats.LeagueDashPlayerStats(season=full_season)
        return self.parse_player_stats(stats)

    def get_current_season_stats(self, last_range):
        current_season = self.get_current_season_full()
        time_to_subtract = None
        if last_range == "week":
            time_to_subtract = timedelta(days=7)
        elif last_range == "month":
            time_to_subtract = timedelta(days=30.4375)

        if not time_to_subtract:
            stats = leaguedashplayerstats.LeagueDashPlayerStats(season=current_season)
            return self.parse_player_stats(stats)

        date_from = datetime.today() - time_to_subtract
        stats = leaguedashplayerstats.LeagueDashPlayerStats(
            season=current_season, date_from_nullable=date_from
        )
        return self.parse_player_stats(stats)

    def get_player_projections(self, fantasy_coeffs):
        if not hasattr(self, "player_projections"):
            self.fetch_player_projections(fantasy_coeffs)
        return self.player_projections

    def fetch_player_projections(self, fantasy_coeffs):
        if hasattr(self, "player_projections"):
            return

        current_season = self.get_current_season()

        print(f"Fetching {current_season - 3} season stats...")
        season_stats_3 = self.get_season_stats(current_season - 3)

        print(f"Fetching {current_season - 2} season stats...")
        season_stats_2 = self.get_season_stats(current_season - 2)

        print(f"Fetching {current_season - 1} season stats...")
        season_stats_1 = self.get_season_stats(current_season - 1)

        print("Fetching current season stats...")
        season_stats = self.get_current_season_stats("season")

        print("Fetching past month stats...")
        month_stats = self.get_current_season_stats("month")

        print("Fetching past week stats...")
        week_stats = self.get_current_season_stats("week")

        for player_id, player_season_stats in season_stats.items():
            prev_season_stats = []

            if player_id in season_stats_3.keys():
                prev_season_stats.append(
                    {"weight": 1, "stats": season_stats_3[player_id]}
                )

            if player_id in season_stats_2.keys():
                prev_season_stats.append(
                    {"weight": 2.5, "stats": season_stats_2[player_id]}
                )

            if player_id in season_stats_1.keys():
                prev_season_stats.append(
                    {"weight": 6.25, "stats": season_stats_1[player_id]}
                )

            age_adjustment = 1 + 0.015 * (PEAK_AGE - player_season_stats["AGE"])
            preseason_projection = age_adjustment * calc_player_projection(
                prev_season_stats, fantasy_coeffs
            )

            current_season_stats = []

            current_season_stats.append({"weight": 1, "stats": player_season_stats})

            if player_id in month_stats.keys():
                current_season_stats.append(
                    {"weight": 3, "stats": month_stats[player_id]}
                )

            if player_id in week_stats.keys():
                current_season_stats.append(
                    {"weight": 12, "stats": week_stats[player_id]}
                )

            current_projection = calc_player_projection(
                current_season_stats, fantasy_coeffs
            )

            player_season_stats["FP_PROJECTION_PRESEASON"] = preseason_projection
            player_season_stats["FP_PROJECTION_CURRENT"] = current_projection

        self.player_projections = key_by(season_stats.values(), "PLAYER_NAME")
