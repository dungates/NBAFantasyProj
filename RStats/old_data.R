# Some shit doesnt work without this idk lol
Sys.setenv("VROOM_CONNECTION_SIZE" = 999999999)
# PLAYER, TEAM, AGE, GP, MIN, PTS, FGM, FGA, 3PM, 3PA, FTM, FTA, OREB, DREB, AST, TOV, STL, BLK, PF
df <- as.data.frame(nbastatR::bref_players_stats(seasons = 2000:2021, tables = c("totals")))
# Coefficients
# coefs <- tibble::tibble(ptsTotals = 1,
#                         trbTotals = 1.2,
#                         astTotals = 1.5,
#                         stlTotals = 3,
#                         blkTotals = 3,
#                         tovTotals = -1,
#                         fg3mTotals = 1)
df <- df %>%
  dplyr::mutate(fantasy_points = ptsTotals + trbTotals*1.2 + astTotals*1.5 + stlTotals*3 + blkTotals*3 + tovTotals*-1 + fg3mTotals*1)
# Write to csv
readr::write_csv(df, "Data/player_season_totals.csv")


df %>% 
  arrange(desc(fantasy_points)) %>% 
  filter(yearSeason == "")
  slice(c(1:10)) %>% 
  select(namePlayer, fantasy_points, urlPlayerHeadshot) %>% 
  # reactable::reactable()
  gt::gt() %>%
  data_color(
    columns = c(fantasy_points),
    colors = scales::col_numeric(
      palette = paletteer::paletteer_d(
        palette = "ggsci::red_material"
      ) %>% as.character(),
      domain = NULL
    )
  ) %>%
  text_transform(
    locations = cells_body(columns = urlPlayerHeadshot),
    fn = function(x) {
      web_image(
        url = x,
        height = as.numeric(50)
      )
    }
  )
