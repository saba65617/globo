library(shiny)

# Set the host and port for the Shiny app
options(shiny.host = "0.0.0.0")
options(shiny.port = 5000)

# Source the app.R file to run the application
source("app.R")