library(shiny)
library(tidyverse)
library(ggimage)

# load the data from the csv file
complexity_data <- read_csv("complexity_change.csv") %>%
  mutate(script = factor(script, levels = c("Oracle", "Bronze", "Seal", "Traditional", "Simplified"))) %>%
  mutate(image_path= paste0("images/", image_path))

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

    ggplot(selected_char , aes(x = script, y = complexity, group = character)) +
      geom_point() +
      geom_line() +
      geom_image( aes(x=script, y=0 + complexity, image = image_path),
                  size = 0.15, by = "height", asp = (6+0.5)/4
      ) +
      scale_y_continuous(expand = expansion(mult = 0.1)) +
      labs(title = paste("Complexity over time of ", input$character))
   }
  })
}

shinyApp(ui = ui, server = server)

