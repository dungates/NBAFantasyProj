Sys.setenv("VROOM_CONNECTION_SIZE" = 999999999)
averages_df <- nbastatR::bref_players_stats(2022, tables = c("per_game", "advanced"), widen = T, assign_to_environment = F)
totals_df <- nbastatR::bref_players_stats(2022, tables = c("totals", "advanced"), widen = T, assign_to_environment = F)
# Coefficients
pts_coef <- 1
trb_coef <- 1.2
ast_coef <- 1.5
stl_coef <- 3
blk_coef <- 3
tov_coef <- -1
fg3m_coef <- 1
# Add fantasy points column
totals_df <- totals_df %>%
  dplyr::mutate(fantasy_points = ptsTotals*pts_coef + trbTotals*trb_coef + astTotals*ast_coef + stlTotals*stl_coef + blkTotals*blk_coef + tovTotals*tov_coef + fg3mTotals*fg3m_coef)
averages_df <- averages_df %>%
  dplyr::mutate(fantasy_points = ptsPerGame*pts_coef + trbPerGame*trb_coef + astPerGame*ast_coef + stlPerGame*stl_coef + blkPerGame*blk_coef + tovPerGame*tov_coef + fg3mPerGame*fg3m_coef)
readr::write_csv(averages_df, "Data/latest_season_averages.csv")
readr::write_csv(totals_df, "Data/latest_season_totals.csv")