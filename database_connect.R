con <- DBI::dbConnect(RSQLite::SQLite(), dbname = "nba.db")
library(magrittr)
upload_data <- readr::read_csv("Data/player_season_totals.csv")

RSQLite::dbWriteTable(conn = con, name = "player_seasons", value = upload_data, overwrite = TRUE)
