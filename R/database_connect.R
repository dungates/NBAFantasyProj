# Duplicate in data folder and database
database_connect <- function(upload_data, name) {
  con <- DBI::dbConnect(RSQLite::SQLite(), dbname = "nba.db")
  
  # upload_data <- readr::write_csv(paste0("Data/", name, ".csv"))
  
  RSQLite::dbWriteTable(conn = con, name = name, value = upload_data, overwrite = TRUE)
}


