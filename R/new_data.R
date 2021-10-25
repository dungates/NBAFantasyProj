new_df <- nbastatR::bref_players_stats(2022, tables = "totals")
readr::write_csv(new_df, "Data/latest_season.csv")