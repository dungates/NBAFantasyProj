#
# This is a Shiny web application. You can run the application by clicking
# the 'Run App' button above.
#
# Find out more about building applications with Shiny here:
#
#    http://shiny.rstudio.com/
#

library(shiny)
library(tidyverse)
library(tidymodels)
library(gt)
df <- readr::read_csv(here::here("Data/player_season_totals.csv"))

# Define UI for application that draws a histogram
ui <- fluidPage(

    # Application title
    titlePanel("NBA Fantasy Data"),

    # Sidebar with a slider input for number of bins 
    sidebarLayout(
        sidebarPanel(
            selectizeInput("year",
                        "Select a year:",
                        choices = 2000:2021,
                        selected = 2021,
                        multiple = T,
                        options = list(plugins= list('remove_button')))
        ),

        # Show a plot of the generated distribution
        mainPanel(
           gt_output("points_plot")
        )
    )
)

# Define server logic required to draw a histogram
server <- function(input, output) {
    
    filtered_df <- reactive({
        gt_df <- df %>% 
            arrange(desc(fantasy_points)) %>% 
            filter(yearSeason %in% input$year) %>%
            select(namePlayer, fantasy_points, urlPlayerHeadshot, slugSeason) %>%
            slice(c(1:10)) %>%
            mutate(Rank = paste0("#", row_number())) %>%
            relocate(Rank, .before = 1)
        
    })
    
    output$points_plot <- render_gt({
        filtered_df() %>%
            gt::gt() %>%
            cols_label(namePlayer = "Name", 
                       fantasy_points = "Fantasy Points",
                       urlPlayerHeadshot = "Player",
                       slugSeason = "Season") %>%
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
            ) %>%
            DGThemes::gt_theme_duncan()
        # mtcars %>%
        #     slice(c(1:10)) %>%
        #     gt::gt()
    })
}

# Run the application 
shinyApp(ui = ui, server = server)
