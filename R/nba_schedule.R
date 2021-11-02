# Get Schedule and write to database

Sys.setenv("VROOM_CONNECTION_SIZE" = 999999999)
schedule <- nbastatR::current_schedule() %>%
  dplyr::filter(dateGame >= as.Date("2021-10-19"))
readr::write_csv(schedule, here::here("Data/schedule_2022.csv"))

con <- DBI::dbConnect(RSQLite::SQLite(), dbname = "nba.db")

schedule <- readr::read_csv("Data/schedule_2022.csv")

RSQLite::dbWriteTable(conn = con, name = "schedules", value = schedule, overwrite = TRUE)
# Get team names and ids and write to database

nbastatR::assign_nba_teams()
teams <- df_dict_nba_teams %>%
  dplyr::slice(-c(1:48)) %>%
  dplyr::arrange(slugTeam) %>%
  dplyr::select(nameTeam, slugTeam, cityTeam, teamNameFull, idTeam)
readr::write_csv(teams, here::here("Data/teams_ids.csv"))

RSQLite::dbWriteTable(conn = con, name = "teams", value = teams, overwrite = TRUE)
