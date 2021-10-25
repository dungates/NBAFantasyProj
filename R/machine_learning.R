library(tidyverse)
library(tidymodels)
library(usemodels)
df <- readr::read_csv(here::here("Data/player_season_totals.csv"))

normal_df <- df %>%
  mutate(id = slugPlayerSeason) %>%
  transmute(id,
            count_games = countGames,
            count_games_started = countGamesStarted,
            pct_fg = pctFG,
            pct_fg3 = pctFG3,
            pct_fg2 = pctFG2,
            pct_efg = pctEFG,
            pct_ft = pctFT,
            minutes = minutesTotals,
            fgm_total = fgmTotals,
            fga_total = fgaTotals,
            fg3m_totals = fg3mTotals,
            fg3a_totals = fg3aTotals,
            fg2m_totals = fg2mTotals,
            fg2a_totals = fg2aTotals,
            ftm_totals = ftmTotals,
            fta_totals = ftaTotals,
            orb_totals = orbTotals,
            drb_totals = drbTotals,
            trb_totals = trbTotals,
            ast_totals = astTotals,
            stl_totals = stlTotals,
            blk_totals = blkTotals,
            tov_totals = tovTotals,
            pf_totals = pfTotals,
            pts_totals = ptsTotals,
            fantasy_points = fantasy_points)

advanced_df <- df %>%
  mutate(id = slugPlayerSeason) %>%
  transmute(ratioPER,
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

set.seed(123)
nba_split <- initial_split(final_df)
nba_train <- training(nba_split)
nba_test <- testing(nba_split)

# usemodels::use_xgboost(fantasy_points ~ ., data = nba_train)

xgboost_recipe <-
  recipe(formula = fantasy_points ~ ., data = nba_train) %>%
  step_novel(all_nominal(), -all_outcomes()) %>%
  step_dummy(all_nominal(), -all_outcomes(), one_hot = TRUE) %>%
  step_zv(all_predictors()) %>%
  step_normalize(all_predictors()) %>%
  update_role(id, new_role = "id")

xgboost_spec <-
  boost_tree(
    trees = tune(), 
    mtry = tune(),
    min_n = tune(), 
    tree_depth = tune(), 
    learn_rate = tune(),
    loss_reduction = tune(), 
    sample_size = tune()
  ) %>%
  set_mode("regression") %>%
  set_engine("xgboost")

xgboost_workflow <-
  workflow() %>%
  add_recipe(xgboost_recipe) %>%
  add_model(xgboost_spec)

set.seed(123)
nba_folds <- vfold_cv(nba_train)

all_cores <- parallel::detectCores(logical = FALSE)

library(doParallel)
cl <- makePSOCKcluster(all_cores)
registerDoParallel(cl)

xgb_res <- tune_grid(
  xgboost_workflow,
  resamples = nba_folds,
  control = control_grid(save_pred = T)
)

# Check out metrics
collect_metrics(xgb_res)
# Visualize rmse and rsq
autoplot(xgb_res)
ggsave(here::here("images/metrics/autoplot_1000_1.png"), height = 10, width = 10)


# Look at rmse
xgb_res %>%
  collect_metrics() %>%
  filter(.metric == "rmse") %>%
  select(mean, mtry:sample_size) %>%
  pivot_longer(mtry:sample_size,
               values_to = "value",
               names_to = "parameter"
  ) %>%
  ggplot(aes(value, mean, color = parameter)) +
  geom_line(alpha = 0.8, show.legend = FALSE) +
  facet_wrap(~parameter, scales = "free_x") +
  labs(x = NULL, y = "RMSE") +
  DGThemes::theme_premium_gs()

# Best model selection
nba_best_model <- select_best(xgb_res, "rmse")
print(nba_best_model)

# Finalize model
nba_final_model <- finalize_model(xgboost_spec, nba_best_model)
nba_workflow_final <- xgboost_workflow %>% update_model(nba_final_model)
nba_xgb_fit <- fit(nba_workflow_final, data = nba_train)

# Evaluate model

pred <- 
  predict(nba_xgb_fit, nba_test) %>% 
  mutate(modelo = "XGBoost",
         .pred = exp(.pred)) %>% 
  bind_cols(nba_test %>% select(fantasy_points))

g1 <- 
  pred %>% 
  ggplot(aes(x = .pred, y = fantasy_points))+
  geom_point()+ 
  geom_abline(intercept = 0, col = "red")


g2 <- 
  pred %>% 
  select(.pred, fantasy_points) %>% 
  gather(key, value) %>% 
  ggplot(aes(x=value, volor = key, fill = key)) + 
  geom_density(alpha=.2)+ 
  labs(x = "", y = "")
library(patchwork)
g1 / g2
