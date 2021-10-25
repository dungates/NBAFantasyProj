# Some shit doesnt work without this idk lol
Sys.setenv("VROOM_CONNECTION_SIZE" = 999999999)
# TOTALS GIVES PLAYER, TEAM, AGE, GP, MIN, PTS, FGM, FGA, 3PM, 3PA, FTM, FTA, OREB, DREB, AST, TOV, STL, BLK, PF
# ADVANCED GIVES minutes, ratioPER, pctTrueShooting, pct3PRate, pctFTRate, pctORB, pctDRB, pctTRB, pctAST, pctSTL, pctBLK, pctTOV, pctUSG, ratioOWS, ratioDWS, ratioWS, ratioWSPer48, ratioOBPM, ratioDBPM, ratioBPM, ratioVORP, countTeamsPlayerSeason
df <- as.data.frame(nbastatR::bref_players_stats(seasons = 2000:2021, tables = c("totals", "advanced"), widen = TRUE, assign_to_environment = F))
# Coefficients
pts_coef <- 1
trb_coef <- 1.2
ast_coef <- 1.5
stl_coef <- 3
blk_coef <- 3
tov_coef <- -1
fg3m_coef <- 1
# Add fantasy points column
df <- df %>%
  dplyr::mutate(fantasy_points = ptsTotals*pts_coef + trbTotals*trb_coef + astTotals*ast_coef + stlTotals*stl_coef + blkTotals*blk_coef + tovTotals*tov_coef + fg3mTotals*fg3m_coef)
# Write to csv
readr::write_csv(df, "Data/player_season_totals.csv")
