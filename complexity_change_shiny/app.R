#Write a shiny app with a line graph that displays data from a file on my computer called character_complexity.csv. The file contains three columns: character, period and complexity.  First, add a side bar with a dropdown that lets users choose which character they want to plot. The line graph should show period on the x-axis and character on the y-axis.


#rsconnect::deployApp(here("complexity_change_shiny"))

library(shiny)
library(tidyverse)

# load the data from the csv file
complexity_data <- read_csv("complexity_change.csv") %>%
  mutate(period = factor(period, levels = c("Oracle", "Bronze", "Seal", "Simplified", "Traditional")))
types <-  c("pictographic", "pictologic", "pictosynthetic", "pictophonetic", "other")

# set plot theme
chartheme <-  theme_classic(base_size = 14)  +
  theme(strip.background = element_blank())
theme_set(chartheme)

# create a shiny app
ui <- fluidPage(
  # add a sidebar with a dropdown menu that lets the user choose a character
  sidebarLayout(
    sidebarPanel(
      uiOutput("character"),
      radioButtons("type", "Character Type", types, selected = "pictographic")
    ),
    # add the line graph to the main panel
    mainPanel(
      plotOutput("complexity_plot")
    )
  )
)



server <- function(input, output) {

  # Filter the characters based on the selected type
  data_filtered <- reactive({
    complexity_data %>%
      filter(type == input$type)
  })

  output$character <- renderUI({
    selectizeInput("character", "Choose a character:", unique(data_filtered()$dropdown_label))
  })

  # create the line graph
  output$complexity_plot <- renderPlot({
   if (length(input$character) > 0) { # don't plot anything until a character has been selected
     selected_char <- data_filtered() %>%
        filter(dropdown_label== input$character)

    ggplot(selected_char , aes(x = period, y = complexity, group = character)) +
      geom_point() +
      geom_line() +
      labs(title = paste("Complexity over time of ", input$character))
   }
  })
}

#selectizeInput("character", "Choose a character:", choices = NULL)

#server <- function(input, output) {
#  # create a reactive object that filters the data based on the selected character
#  selected_data <- reactive({
#    complexity_data %>%
#      filter(character == input$character)
#  })

#  # create the line graph
#  output$complexity_plot <- renderPlot({
#    ggplot(selected_data(), aes(x = period, y = complexity, group = character)) +
#      geom_point() +
#      geom_line() +
#      labs(title = paste("Complexity over time of ", input$character))
#  })
#}


shinyApp(ui = ui, server = server)

