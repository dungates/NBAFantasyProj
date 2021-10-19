library(tidyverse)
library(tidymodels)
library(usemodels)
df <- readr::read_csv(here::here("Data/player_season_totals.csv"))

final_df <- df %>%
  mutate(id = factor(stringr::str_replace_all(paste0(stringr::str_to_lower(yearSeason), "_", stringr::str_to_lower(namePlayer)), " ", ""))) %>%
  select(id, where(is.numeric))

set.seed(123)
nba_split <- initial_split(final_df %>% slice_sample(n = 10))
nba_train <- training(nba_split)
nba_test <- testing(nba_split)

# usemodels::use_xgboost(fantasy_points ~ ., data = nba_train)

xgboost_recipe <-
  recipe(formula = fantasy_points ~ ., data = nba_train) %>%
  step_novel(all_nominal(), -all_outcomes()) %>%
  step_dummy(all_nominal(), -all_outcomes(), one_hot = TRUE) %>%
  step_zv(all_predictors()) %>%
  update_role(id, new_role = "id")

xgboost_spec <-
  boost_tree(
    trees = tune(), 
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

xgb_res <- tune_grid(
  xgboost_workflow,
  resamples = nba_folds,
  control = control_grid(save_pred = T)
)

collect_metrics(xgb_res)

xgb_res %>%
  collect_metrics() %>%
  filter(.metric == "roc_auc") %>%
  select(mean, mtry:sample_size) %>%
  pivot_longer(mtry:sample_size,
               values_to = "value",
               names_to = "parameter"
  ) %>%
  ggplot(aes(value, mean, color = parameter)) +
  geom_point(alpha = 0.8, show.legend = FALSE) +
  facet_wrap(~parameter, scales = "free_x") +
  labs(x = NULL, y = "AUC")
