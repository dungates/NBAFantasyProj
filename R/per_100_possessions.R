library(tictoc)
library(httr)
library(tidyverse)

tic()

h <- c("x-nba-stats-origin" = "stats",
       "x-nba-stats-token" = "true",
       "origin" = "refer")

df <- httr::GET(url = "https://stats.nba.com/stats/leaguedashplayerstats?College=&Conference=&Country=&DateFrom=&DateTo=&Division=&DraftPick=&DraftYear=&GameScope=&GameSegment=&Height=&LastNGames=0&LeagueID=00&Location=&MeasureType=Base&Month=0&OpponentTeamID=0&Outcome=&PORound=0&PaceAdjust=N&PerMode=PerGame&Period=0&PlayerExperience=&PlayerPosition=&PlusMinus=N&Rank=N&Season=2021-22&SeasonSegment=&SeasonType=Regular+Season&ShotClockRange=&StarterBench=&TeamID=0&TwoWay=0&VsConference=&VsDivision=&Weight=",
                httr::add_headers(.headers = h),
                user_agent("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36"))

all_player_stats <- content(df, as = "parsed", type = "application/json")

split_players <- all_player_stats$resultSets

headers <- split_players[[1]]$headers %>% unlist() %>% as.vector()

values <- split_players[[1]]$rowSet

final_df <- purrr::map_dfr(values, ~ tibble::as_tibble(t(.x)))

colnames(final_df) <- headers
toc()

database_connect <- function(upload_data, name) {
  con <- DBI::dbConnect(RSQLite::SQLite(), dbname = "nba.db")
  
  # upload_data <- readr::write_csv(paste0("Data/", name, ".csv"))
  
  RSQLite::dbWriteTable(conn = con, name = name, value = upload_data, overwrite = TRUE)
}

database_connect(upload_data = final_df, name = "player_tables_2022")
