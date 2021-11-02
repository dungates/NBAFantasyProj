library(tidyverse)
library(tidymodels)
library(gt)
library(DGThemes)
library(nbastatR)
#### TO ADD TO MODEL ONCE ENOUGH GAMES HAPPEN FOR GAME BY GAME PREDICTIONS ####
#### Get all game ids so far this season ####
# game_ids <- nbastatR::current_schedule() %>%
#   filter(dateGame < Sys.Date()) %>%
#   distinct(idGame) %>%
#   as_vector()

#### Get box scores for games this season and calculate fantasy points ####
# box_scores <- nbastatR::box_scores(game_ids, assign_to_environment = F)

# Read in all games so far this season
daily_df <- readr::read_csv(here::here("Data/latest_season_averages.csv"))

# Get advanced stats by team this season and select just drtg and team name
defense_stats <- nbastatR::teams_players_stats(seasons = 2022, 
                                               types = c("team"), 
                                               tables = "general", 
                                               measures = "Advanced", 
                                               assign_to_environment = F) %>%
  unnest(dataTable) %>%
  select(nameTeam, drtg)

# NBA team names and abbreviations for joining later
team_names <- readr::read_csv(here::here("Data/nba_teams.csv"))

# Get todays games
todays_games <- nbastatR::current_schedule() %>%
  filter(dateGame == Sys.Date())

# Get all combos of todays games
team_combos <- todays_games %>% select(slugTeamBREF = slugTeamHome, opponent = slugTeamAway) %>%
  bind_rows(todays_games %>% select(slugTeamBREF = slugTeamAway, opponent = slugTeamHome))

# Combine todays games and todays defense
todays_defense <- todays_games %>%
  select(nameTeamAway, nameTeamHome) %>% # home team and away team
  pivot_longer(everything(), names_to = "home_away", values_to = "nameTeam") %>% # Make dataframe have all team names in one column and away/home in separate column
  left_join(team_names, by = "nameTeam") %>%
  mutate(nameTeam = stringr::str_replace_all(nameTeam, c("Los Angeles Clippers" = "LA Clippers"))) %>% # Rename since there is a difference here
  inner_join(defense_stats, by = c("nameTeam")) %>% # only join on games happening today
  mutate(home_away = stringr::str_replace_all(home_away, c("nameTeamAway" = "Away", "nameTeamHome" = "Home"))) %>%
  # This isn't actually opponents drtg, but it will be when I bind the data later
  select(home_away, slugTeam, opponent_drtg = drtg)

final_df <- daily_df %>%
  left_join(team_combos, by = c("slugTeamBREF")) %>%
  inner_join(todays_defense, by = c("opponent" = "slugTeam"))

advanced_df <- final_df %>%
  mutate(id = slugPlayerSeason) %>%
  transmute(player = namePlayer,
            pct_fg = pctFG,
            pct_fg3 = pctFG3,
            pct_fg2 = pctFG2,
            pct_efg = pctEFG,
            pct_ft = pctFT,
            minutes = minutesPerGame,
            fgm_pergame = fgmPerGame,
            fga_pergame = fgaPerGame,
            fg3m_pergame = fg3mPerGame,
            fg3a_pergame = fg3aPerGame,
            fg2m_pergame = fg2mPerGame,
            fg2a_pergame = fg2aPerGame,
            ftm_pergame = ftmPerGame,
            fta_pergame = ftaPerGame,
            orb_pergame = orbPerGame,
            drb_pergame = drbPerGame,
            trb_pergame = trbPerGame,
            ast_pergame = astPerGame,
            stl_pergame = stlPerGame,
            blk_pergame = blkPerGame,
            tov_pergame = tovPerGame,
            pf_pergame = pfPerGame,
            pts_pergame = ptsPerGame,
            ratio_per = ratioPER,
            pct_true_shooting = pctTrueShooting,
            pct_3p_rate = pct3PRate,
            pct_ft_rate = pctFTRate,
            pct_orb = pctORB,
            pct_drb = pctDRB,
            pct_trb = pctTRB,
            pct_ast = pctAST,
            pct_stl = pctSTL,
            pct_blk = pctBLK,
            pct_tov = pctTOV,
            pct_usg = pctUSG,
            ratio_ows = ratioOWS,
            ratio_dws = ratioDWS,
            ratio_ws = ratioWS,
            ratio_ws_per_48 = ratioWSPer48,
            ratio_obpm = ratioOBPM,
            ratio_dbpm = ratioDBPM,
            ratio_bpm = ratioBPM,
            ratio_vorp = ratioVORP,
            fantasy_points = fantasy_points)


set.seed(2021)
nba_split <- initial_split(advanced_df)
nba_train <- training(nba_split)
nba_test <- testing(nba_split)

lm_spec <- linear_reg() %>%
  set_engine(engine = "lm")

rec <- recipe(fantasy_points ~ ., data = nba_train) %>%
  update_role(player, new_role = "id") %>% # Make player name into id
  step_corr(all_numeric(), -all_outcomes()) %>% # Remove all multicolinear variables
  prep()

lm_wf <- workflow() %>%
  add_model(lm_spec) %>%
  add_recipe(rec)

lm_fit <- lm_wf %>%
  fit(data = nba_train)

# rf_spec <- rand_forest(mode = "regression") %>%
#   set_engine(engine = "ranger")
# 
# rf_wf <- workflow() %>%
#   add_model(rf_spec) %>%
#   add_recipe(rec)
# 
# rf_fit <- rf_wf %>%
#   fit(data = nba_train)
# 
# results_train <- lm_fit %>%
#   predict(new_data = nba_train) %>%
#   mutate(truth = nba_train$fantasy_points,
#          model = "lm") %>%
#   bind_rows(rf_fit %>%
#               predict(new_data = nba_train) %>%
#               mutate(truth = nba_train$fantasy_points,
#                      model = "rf"))
# 
# results_test <- lm_fit %>%
#   predict(new_data = nba_test) %>%
#   mutate(truth = nba_test$fantasy_points,
#          model = "lm") %>%
#   bind_rows(rf_fit %>%
#               predict(new_data = nba_test) %>%
#               mutate(truth = nba_test$fantasy_points,
#                      model = "rf"))

#### Model comparisons, lm model is for sure better ####
# results_test %>%
#   group_by(model) %>%
#   rmse(truth = truth, estimate = .pred)

# Table to auto-email maybe?
advanced_df %>%
  arrange(desc(fantasy_points)) %>%
  select(player, fantasy_points) %>%
  mutate(rank = row_number(), .before = 1) %>%
  gt::gt() %>%
  gt::cols_label(
    rank = "Rank",
    player = "Player",
    fantasy_points = "Fantasy Points Projection Tonight"
  ) %>%
  DGThemes::gt_theme_duncan()
