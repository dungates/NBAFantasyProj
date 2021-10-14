# Some shit doesnt work without this idk lol
Sys.setenv("VROOM_CONNECTION_SIZE" = 999999999)
# PLAYER, TEAM, AGE, GP, MIN, PTS, FGM, FGA, 3PM, 3PA, FTM, FTA, OREB, DREB, AST, TOV, STL, BLK, PF
df <- as.data.frame(nbastatR::bref_players_stats(seasons = 2000:2021, tables = c("totals")))
# Write to csv
readr::write_csv(df, "Data/player_season_totals.csv")