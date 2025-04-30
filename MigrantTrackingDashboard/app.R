library(shiny)
library(shinydashboard)
library(shinythemes)
library(readr)
library(dplyr)
library(plotly)
library(leaflet)
library(DT)
library(ggplot2)
library(tidyr)
library(RColorBrewer)
library(DBI)
library(RPostgres)

# Source helper files
source("data_processing.R")
source("visualization.R")
source("utils.R")
source("database_connection.R")

# UI definition
ui <- fluidPage(
  theme = shinytheme("cosmo"),
  
  # Custom CSS for modern dashboard theme similar to the image
  tags$head(
    tags$style(HTML("
      @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
      
      body {
        font-family: 'Inter', sans-serif;
        background-color: #f0f2f5;
        color: #333;
      }
      
      /* Dark theme sidebar */
      .sidebar {
        background-color: #1c2333;
        color: white;
        padding: 20px;
        min-height: 100vh;
        box-shadow: 2px 0 10px rgba(0,0,0,0.1);
      }
      
      .sidebar .logo {
        font-size: 24px;
        font-weight: 600;
        margin-bottom: 30px;
        color: white;
        display: flex;
        align-items: center;
      }
      
      .sidebar .logo-icon {
        background-color: #6366f1;
        width: 32px;
        height: 32px;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-right: 10px;
      }
      
      /* Navigation menu styling */
      .nav-menu {
        margin: 20px 0;
      }
      
      .nav-item {
        display: flex;
        align-items: center;
        padding: 12px 15px;
        border-radius: 10px;
        margin-bottom: 8px;
        color: #a0aec0;
        cursor: pointer;
        transition: all 0.2s ease;
        font-size: 14px;
      }
      
      .nav-item i {
        margin-right: 12px;
        width: 20px;
        text-align: center;
        font-size: 16px;
      }
      
      .nav-item:hover {
        background-color: rgba(255, 255, 255, 0.05);
        color: #e2e8f0;
        transform: translateX(3px);
      }
      
      .nav-item.active {
        background: linear-gradient(90deg, rgba(99, 102, 241, 0.15), rgba(99, 102, 241, 0.05));
        color: white;
        font-weight: 500;
        box-shadow: -3px 0 0 #6366f1;
      }
      
      .sidebar .shiny-input-container {
        margin-bottom: 25px;
      }
      
      /* Custom styling for filter controls */
      .sidebar .shiny-input-container .control-label {
        color: #e2e8f0;
        font-size: 13px;
        font-weight: 500;
        margin-bottom: 8px;
      }
      
      .sidebar .form-control {
        background-color: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        color: white;
        border-radius: 8px;
      }
      
      .sidebar .form-control:focus {
        border-color: #6366f1;
        box-shadow: 0 0 0 1px rgba(99, 102, 241, 0.4);
      }
      
      .sidebar .selectize-input {
        background-color: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        color: white;
        border-radius: 8px;
      }
      
      .sidebar .selectize-dropdown {
        background-color: #1c2333;
        border: 1px solid rgba(255, 255, 255, 0.1);
        color: white;
        border-radius: 8px;
      }
      
      .sidebar .selectize-dropdown-content .option {
        padding: 10px;
      }
      
      .sidebar .selectize-dropdown-content .option:hover {
        background-color: rgba(99, 102, 241, 0.2);
      }
      
      .sidebar .selectize-dropdown-content .option.active {
        background-color: rgba(99, 102, 241, 0.4);
      }
      
      /* Range slider styling */
      .sidebar .js-irs-0 .irs-bar {
        background: #6366f1;
        border-color: #6366f1;
      }
      
      .sidebar .js-irs-0 .irs-single,
      .sidebar .js-irs-0 .irs-from,
      .sidebar .js-irs-0 .irs-to {
        background: #6366f1;
      }
      
      .sidebar .js-irs-0 .irs-handle {
        border-color: #6366f1;
      }
      
      .sidebar h3 {
        color: #a0aec0;
        font-size: 14px;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-top: 30px;
        margin-bottom: 15px;
        font-weight: 600;
      }
      
      /* Main content area */
      .main-content {
        padding: 25px;
        background-color: #f0f2f5;
      }
      
      /* Header area with profile */
      .header-bar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 10px 0;
        margin-bottom: 20px;
      }
      
      .profile-section {
        display: flex;
        align-items: center;
      }
      
      .profile-img {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        background-color: #e2e8f0;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #6366f1;
        font-weight: bold;
        margin-left: 15px;
      }
      
      /* Dashboard cards */
      .metric-box {
        background-color: white;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 2px 12px rgba(0,0,0,0.04);
        margin-bottom: 20px;
        text-align: center;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
      }
      
      .metric-box:hover {
        transform: translateY(-3px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.08);
      }
      
      .metric-box.purple {
        background: linear-gradient(135deg, #6366f1, #8b5cf6);
        color: white;
      }
      
      .metric-box.teal {
        background: linear-gradient(135deg, #14b8a6, #2dd4bf);
        color: white;
      }
      
      .metric-box.orange {
        background: linear-gradient(135deg, #f97316, #fb923c);
        color: white;
      }
      
      .metric-box.green {
        background: linear-gradient(135deg, #22c55e, #4ade80);
        color: white;
      }
      
      .tab-panel {
        background-color: white;
        border-radius: 12px;
        padding: 25px;
        box-shadow: 0 2px 12px rgba(0,0,0,0.04);
        margin-top: 20px;
      }
      
      .value-box {
        font-size: 32px;
        font-weight: 700;
        color: inherit;
        margin-top: 5px;
      }
      
      .title-box {
        font-size: 14px;
        color: inherit;
        opacity: 0.9;
        font-weight: 500;
      }
      
      /* Navigation tabs */
      .nav-tabs {
        border-bottom: none;
        margin-bottom: 20px;
      }
      
      .nav-tabs > li > a {
        background-color: #f8f9fa;
        margin-right: 8px;
        border-radius: 8px 8px 0 0;
        color: #64748b;
        border: none;
        padding: 12px 20px;
        font-weight: 500;
      }
      
      .nav-tabs > li.active > a {
        background-color: white;
        color: #6366f1;
        font-weight: 600;
        border-bottom: 3px solid #6366f1;
      }
      
      .nav-tabs > li > a:hover {
        background-color: #e2e8f0;
        border: none;
      }
      
      .page-header {
        border-bottom: none;
        margin-bottom: 25px;
        padding-bottom: 10px;
      }
      
      .page-header h1 {
        font-weight: 700;
        color: #334155;
        font-size: 28px;
      }
      
      /* Charts and visualizations */
      .chart-container {
        background: white;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 2px 12px rgba(0,0,0,0.04);
        margin-bottom: 25px;
      }
      
      /* Circular progress indicators */
      .progress-circle {
        position: relative;
        width: 100px;
        height: 100px;
        margin: 0 auto;
      }
      
      .progress-circle-bg {
        fill: none;
        stroke: #e2e8f0;
        stroke-width: 8;
      }
      
      .progress-circle-value {
        fill: none;
        stroke: #6366f1;
        stroke-width: 8;
        stroke-linecap: round;
        transform: rotate(-90deg);
        transform-origin: center;
      }
      
      .progress-text {
        font-size: 24px;
        font-weight: bold;
        fill: #334155;
      }
    "))
  ),
  
  # Page layout with sidebar and main content
  fluidRow(
    # Sidebar with filters
    column(
      width = 3,
      div(
        class = "sidebar",
        
        # Logo and title
        div(
          class = "logo",
          div(class = "logo-icon", icon("globe")), 
          "MigrantTracker"
        ),
        
        # Navigation menu
        div(
          class = "nav-menu",
          div(
            class = "nav-item active",
            icon("home"), "Home"
          ),
          div(
            class = "nav-item",
            icon("database"), "Database"
          ),
          div(
            class = "nav-item",
            icon("chart-bar"), "Analytics"
          )
        ),
        
        # Divider
        tags$hr(style = "border-color: #2d3748; margin: 25px 0;"),
        
        # Filters section
        h3("DATA FILTERS"),
        
        # Year Range filter
        uiOutput("yearRangeUI"),
        
        # Region filter
        uiOutput("regionFilterUI"),
        
        # Cause of death filter
        uiOutput("causeFilterUI"),
        
        # Info about data source
        div(
          style = "position: absolute; bottom: 20px; width: 85%;",
          hr(),
          tags$div(
            class = "info-box",
            icon("info-circle"), 
            "Global Missing Migrants Dataset (2014-2024)",
            style = "color: #a0aec0; display: flex; align-items: center; gap: 8px; margin-bottom: 10px;"
          ),
          p("A humanitarian data visualization project", style = "color: #718096; font-size: 12px;")
        )
      )
    ),
    
    # Main content
    column(
      width = 9,
      div(
        class = "main-content",
        
        # Header with profile section
        div(
          class = "header-bar",
          div(
            class = "page-header",
            h1("Missing Migrants Analysis")
          ),
          div(
            class = "profile-section",
            span("Last updated: April 29, 2025", style = "color: #64748b; margin-right: 20px;"),
            div(class = "profile-img", "R")
          )
        ),
        
        # Description panel
        div(
          class = "chart-container",
          style = "margin-bottom: 25px;",
          h4("About this Dashboard", style = "margin-top: 0; color: #334155;"),
          p("This dashboard analyzes global data on missing and deceased migrants between 2014 and 2024. 
             The aim is to explore trends in migrant deaths, highlight affected regions, understand common causes, 
             and visualize the locations where these tragic incidents occurred.", 
             style = "color: #475569; line-height: 1.6;")
        ),
        
        # Key Metrics
        h3("Dashboard Overview", style = "font-weight: 600; color: #334155; margin-bottom: 20px;"),
        fluidRow(
          column(
            width = 3,
            div(
              class = "metric-box purple",
              div(class = "title-box", "TOTAL INCIDENTS"),
              uiOutput("totalIncidents")
            )
          ),
          column(
            width = 3,
            div(
              class = "metric-box teal",
              div(class = "title-box", "REPORTED DEATHS"),
              uiOutput("totalDeaths")
            )
          ),
          column(
            width = 3,
            div(
              class = "metric-box orange",
              div(class = "title-box", "MISSING PERSONS"),
              uiOutput("totalMissing")
            )
          ),
          column(
            width = 3,
            div(
              class = "metric-box green",
              div(class = "title-box", "TOTAL CASUALTIES"),
              uiOutput("totalCasualties")
            )
          )
        ),
        
        # Protection status donut chart (similar to the image)
        fluidRow(
          column(
            width = 4,
            div(
              class = "chart-container",
              h4("Protection Status", style = "margin-top: 0; color: #334155;"),
              div(
                style = "display: flex; justify-content: center; padding: 15px;",
                div(
                  style = "position: relative; width: 160px; height: 160px;",
                  tags$svg(
                    width = "160", height = "160", viewBox = "0 0 160 160",
                    tags$circle(
                      class = "progress-circle-bg",
                      cx = "80", cy = "80", r = "70"
                    ),
                    tags$circle(
                      class = "progress-circle-value",
                      cx = "80", cy = "80", r = "70",
                      style = "stroke: #6366f1; stroke-dasharray: 440; stroke-dashoffset: 88;" # 80% of 440
                    ),
                    tags$text(
                      class = "progress-text",
                      x = "80", y = "90",
                      "80%",
                      style = "text-anchor: middle;"
                    )
                  ),
                  div(
                    style = "position: absolute; bottom: -30px; width: 100%; text-align: center;",
                    "Average Protection"
                  )
                )
              )
            )
          ),
          column(
            width = 8,
            div(
              class = "chart-container",
              h4("Issue Severity Breakdown", style = "margin-top: 0; color: #334155;"),
              div(
                style = "margin-top: 20px;",
                div(
                  style = "margin-bottom: 15px;",
                  div(style = "display: flex; justify-content: space-between; margin-bottom: 5px;",
                      span("Simple", style = "color: #475569;"),
                      span("50%", style = "color: #334155; font-weight: 500;")),
                  div(style = "width: 100%; height: 8px; background-color: #e2e8f0; border-radius: 4px;",
                      div(style = "width: 50%; height: 100%; background-color: #ef4444; border-radius: 4px;"))
                ),
                div(
                  style = "margin-bottom: 15px;",
                  div(style = "display: flex; justify-content: space-between; margin-bottom: 5px;",
                      span("Medium", style = "color: #475569;"),
                      span("25%", style = "color: #334155; font-weight: 500;")),
                  div(style = "width: 100%; height: 8px; background-color: #e2e8f0; border-radius: 4px;",
                      div(style = "width: 25%; height: 100%; background-color: #f97316; border-radius: 4px;"))
                ),
                div(
                  style = "margin-bottom: 15px;",
                  div(style = "display: flex; justify-content: space-between; margin-bottom: 5px;",
                      span("Complex", style = "color: #475569;"),
                      span("10%", style = "color: #334155; font-weight: 500;")),
                  div(style = "width: 100%; height: 8px; background-color: #e2e8f0; border-radius: 4px;",
                      div(style = "width: 10%; height: 100%; background-color: #6366f1; border-radius: 4px;"))
                )
              )
            )
          )
        ),
        
        # Monthly trends chart
        div(
          class = "chart-container",
          style = "margin-top: 30px;",
          h4("Monthly Activity Trends (2014-2024)", style = "margin-top: 0; color: #334155; display: flex; justify-content: space-between;", 
             tags$div(
               style = "display: flex; align-items: center;",
               tags$span("Nov 2023", style = "font-size: 12px; color: #64748b; background-color: #e2e8f0; padding: 4px 12px; border-radius: 20px;")
             )
          ),
          div(
            style = "margin-top: 20px;",
            plotlyOutput("monthlyOverview", height = "250px")
          )
        ),
        
        # Tabs for detailed visualizations
        div(
          class = "tab-panel",
          h3("Detailed Analysis", style = "font-weight: 600; color: #334155; margin-bottom: 20px;"),
          tabsetPanel(
            id = "visualizationTabs",
            
            # Tab 1: Yearly Trends
            tabPanel(
              "Yearly Trends",
              div(
                class = "chart-container",
                h4("Yearly Trends of Migrant Deaths and Disappearances", style = "margin-top: 0; color: #334155;"),
                div(style = "color: #64748b; font-size: 14px; margin-bottom: 15px;", 
                    "Tracking annual casualties and incident counts over the entire dataset period."),
                plotlyOutput("yearlyTrendChart", height = "400px")
              ),
              
              div(
                class = "chart-container",
                h4("Monthly Heat Distribution", style = "margin-top: 0; color: #334155;"),
                div(style = "color: #64748b; font-size: 14px; margin-bottom: 15px;", 
                    "Heatmap showing monthly patterns and seasonal variations across years."),
                plotlyOutput("monthlyChart", height = "400px")
              )
            ),
            
            # Tab 2: Regional Analysis
            tabPanel(
              "Regional Analysis",
              fluidRow(
                column(
                  width = 6,
                  div(
                    class = "chart-container",
                    h4("Incidents by Region of Origin", style = "margin-top: 0; color: #334155;"),
                    div(style = "color: #64748b; font-size: 14px; margin-bottom: 15px;", 
                        "Top regions where migrants originated from, by casualty count."),
                    plotlyOutput("originRegionChart", height = "350px")
                  )
                ),
                column(
                  width = 6,
                  div(
                    class = "chart-container",
                    h4("Incidents by Region of Incident", style = "margin-top: 0; color: #334155;"),
                    div(style = "color: #64748b; font-size: 14px; margin-bottom: 15px;", 
                        "Regions where incidents occurred, highlighting migration danger zones."),
                    plotlyOutput("incidentRegionChart", height = "350px")
                  )
                )
              ),
              
              div(
                class = "chart-container",
                h4("Top Migration Routes by Casualties", style = "margin-top: 0; color: #334155;"),
                div(style = "color: #64748b; font-size: 14px; margin-bottom: 15px;", 
                    "The deadliest migration routes based on total casualties reported."),
                plotlyOutput("routeChart", height = "500px")
              )
            ),
            
            # Tab 3: Causes of Death
            tabPanel(
              "Causes of Death",
              fluidRow(
                column(
                  width = 5,
                  div(
                    class = "chart-container",
                    h4("Causes of Death Distribution", style = "margin-top: 0; color: #334155;"),
                    div(style = "color: #64748b; font-size: 14px; margin-bottom: 15px;", 
                        "Primary causes of migrant deaths and disappearances."),
                    plotlyOutput("causeChart", height = "400px")
                  )
                ),
                column(
                  width = 7,
                  div(
                    class = "chart-container",
                    h4("Causes of Death by Year", style = "margin-top: 0; color: #334155;"),
                    div(style = "color: #64748b; font-size: 14px; margin-bottom: 15px;", 
                        "Evolution of different causes of death over time."),
                    plotlyOutput("causeYearChart", height = "400px")
                  )
                )
              )
            ),
            
            # Tab 4: Demographics
            tabPanel(
              "Demographics",
              fluidRow(
                column(
                  width = 6,
                  div(
                    class = "chart-container",
                    h4("Gender Distribution", style = "margin-top: 0; color: #334155;"),
                    div(style = "color: #64748b; font-size: 14px; margin-bottom: 15px;", 
                        "Breakdown of casualties by gender, where recorded."),
                    plotlyOutput("genderChart", height = "350px")
                  )
                ),
                column(
                  width = 6,
                  div(
                    class = "chart-container",
                    h4("Age Group Distribution", style = "margin-top: 0; color: #334155;"),
                    div(style = "color: #64748b; font-size: 14px; margin-bottom: 15px;", 
                        "Distribution by age group, highlighting vulnerable populations."),
                    plotlyOutput("ageChart", height = "350px")
                  )
                )
              ),
              div(
                class = "chart-container",
                style = "margin-top: 20px;",
                h4("Demographic Insights", style = "margin-top: 0; color: #334155;"),
                div(style = "background-color: #f8fafc; padding: 15px; border-radius: 8px; border-left: 4px solid #6366f1;",
                    div(style = "font-weight: 600; margin-bottom: 8px; color: #334155;", "Limited Data Available"),
                    div(style = "color: #64748b; line-height: 1.6;", 
                        "Note that demographic data is often incomplete in migration incident reports. 
                        Many casualties remain unidentified, making it difficult to establish accurate demographic profiles.
                        The charts reflect only cases where gender or age information was available.")
                )
              )
            ),
            
            # Tab 5: Geographic Distribution
            tabPanel(
              "Geographic Distribution",
              div(
                class = "chart-container",
                h4("Incident Locations Worldwide", style = "margin-top: 0; color: #334155;"),
                div(style = "color: #64748b; font-size: 14px; margin-bottom: 15px;", 
                    "Interactive map showing the locations of recorded incidents. Each point represents an incident, with the size indicating the number of casualties."),
                leafletOutput("incidentMap", height = "500px")
              ),
              
              div(
                class = "chart-container",
                style = "margin-top: 20px;",
                h4("Countries of Origin Heatmap", style = "margin-top: 0; color: #334155;"),
                div(style = "color: #64748b; font-size: 14px; margin-bottom: 15px;", 
                    "Geographic heat map showing the countries of origin for migrants in the dataset."),
                plotlyOutput("countryHeatmap", height = "450px")
              )
            )
          )
        )
      )
    )
  )
)

# Server logic
server <- function(input, output, session) {
  
  # Establish database connection
  db_conn <- reactiveVal(NULL)
  
  # Initialize the database connection when the app starts
  observe({
    tryCatch({
      conn <- connect_to_database()
      db_conn(conn)
      
      # Register disconnect event when app closes
      onStop(function() {
        if (!is.null(db_conn())) {
          close_database_connection(db_conn())
        }
      })
    }, error = function(e) {
      showNotification(
        paste("Error connecting to database:", e$message),
        type = "error",
        duration = NULL
      )
    })
  })
  
  # Get year range for slider from database
  output$yearRangeUI <- renderUI({
    req(db_conn())
    
    tryCatch({
      year_range <- get_year_range(db_conn())
      min_year <- as.integer(year_range$min)
      max_year <- as.integer(year_range$max)
      
      sliderInput(
        "yearRange",
        "Select Year Range",
        min = min_year,
        max = max_year,
        value = c(min_year, max_year),
        step = 1,
        sep = ""
      )
    }, error = function(e) {
      # Fallback if database query fails
      sliderInput(
        "yearRange",
        "Select Year Range",
        min = 2014,
        max = 2024,
        value = c(2014, 2024),
        step = 1,
        sep = ""
      )
    })
  })
  
  # Region filter from database
  output$regionFilterUI <- renderUI({
    req(db_conn())
    
    tryCatch({
      all_regions <- get_all_regions(db_conn())
      
      selectInput(
        "selectedRegion",
        "Select Region",
        choices = all_regions,
        selected = "All Regions"
      )
    }, error = function(e) {
      selectInput(
        "selectedRegion",
        "Select Region",
        choices = c("All Regions"),
        selected = "All Regions"
      )
    })
  })
  
  # Cause of death filter from database
  output$causeFilterUI <- renderUI({
    req(db_conn())
    
    tryCatch({
      all_causes <- get_all_causes(db_conn())
      
      selectInput(
        "selectedCause",
        "Select Cause of Death",
        choices = all_causes,
        selected = "All Causes"
      )
    }, error = function(e) {
      selectInput(
        "selectedCause",
        "Select Cause of Death",
        choices = c("All Causes"),
        selected = "All Causes"
      )
    })
  })
  
  # Get data from database with filters applied
  filtered_data <- reactive({
    req(db_conn())
    req(input$yearRange)
    
    # Get the data with filters
    data <- get_incident_data(
      db_conn(),
      year_from = input$yearRange[1],
      year_to = input$yearRange[2],
      region = input$selectedRegion,
      cause = input$selectedCause
    )
    
    # Rename columns to match expected format in visualization functions
    names(data) <- gsub("_", " ", names(data))
    names(data) <- tools::toTitleCase(names(data))
    
    # Important column renames to match exact expected format
    data <- data %>% rename(
      `Incident year` = "Incident Year",
      `Reported Month` = "Reported Month",
      `Month Number` = "Month Number",
      `Region of Origin` = "Region Of Origin",
      `Region of Incident` = "Region Of Incident",
      `Country of Origin` = "Country Of Origin", 
      `Number of Dead` = "Number Of Dead",
      `Minimum Estimated Number of Missing` = "Minimum Estimated Number Of Missing",
      `Total Number of Dead and Missing` = "Total Number Of Dead And Missing",
      `Number of Survivors` = "Number Of Survivors",
      `Number of Females` = "Number Of Females",
      `Number of Males` = "Number Of Males",
      `Number of Children` = "Number Of Children",
      `Cause of Death` = "Cause Of Death",
      `Migration route` = "Migration Route"
    )
    
    return(data)
  })
  
  # Key metrics
  output$totalIncidents <- renderUI({
    total <- nrow(filtered_data())
    div(class = "value-box", format(total, big.mark = ","))
  })
  
  output$totalDeaths <- renderUI({
    total <- sum(filtered_data()$`Number of Dead`, na.rm = TRUE)
    div(class = "value-box", format(as.integer(total), big.mark = ","))
  })
  
  output$totalMissing <- renderUI({
    total <- sum(filtered_data()$`Minimum Estimated Number of Missing`, na.rm = TRUE)
    div(class = "value-box", format(as.integer(total), big.mark = ","))
  })
  
  output$totalCasualties <- renderUI({
    total <- sum(filtered_data()$`Total Number of Dead and Missing`, na.rm = TRUE)
    div(class = "value-box", format(as.integer(total), big.mark = ","))
  })
  
  # Visualizations
  
  # Monthly Overview (summary chart in dashboard)
  output$monthlyOverview <- renderPlotly({
    # Get monthly data
    data <- filtered_data()
    
    # Group by month and sum casualties
    monthly_data <- data %>%
      group_by(`Month Number`, `Reported Month`) %>%
      summarise(
        Casualties = sum(`Total Number of Dead and Missing`, na.rm = TRUE),
        .groups = 'drop'
      ) %>%
      arrange(`Month Number`)
    
    # Create more visually appealing bar chart 
    plot_ly(monthly_data, x = ~`Reported Month`, y = ~Casualties, type = "bar", 
            marker = list(color = "#60a5fa",
                          line = list(color = "#3b82f6", width = 0))) %>%
      layout(
        xaxis = list(title = "", showgrid = FALSE),
        yaxis = list(title = "Casualties", showgrid = TRUE, gridcolor = "#f1f5f9",
                     zeroline = FALSE),
        plot_bgcolor = "rgba(0,0,0,0)",
        paper_bgcolor = "rgba(0,0,0,0)",
        margin = list(l = 40, r = 30, t = 10, b = 40),
        hoverlabel = list(bgcolor = "#334155", font = list(color = "white")),
        showlegend = FALSE
      )
  })
  
  # 1. Yearly Trend Chart
  output$yearlyTrendChart <- renderPlotly({
    create_yearly_trend_chart(filtered_data())
  })
  
  # 2. Monthly Chart
  output$monthlyChart <- renderPlotly({
    create_monthly_chart(filtered_data())
  })
  
  # 3. Region Charts
  output$originRegionChart <- renderPlotly({
    create_region_chart(filtered_data(), 'Region of Origin')
  })
  
  output$incidentRegionChart <- renderPlotly({
    create_region_chart(filtered_data(), 'Region of Incident')
  })
  
  # 4. Route Chart
  output$routeChart <- renderPlotly({
    create_route_chart(filtered_data())
  })
  
  # 5. Cause Charts
  output$causeChart <- renderPlotly({
    create_cause_chart(filtered_data())
  })
  
  output$causeYearChart <- renderPlotly({
    create_cause_year_chart(filtered_data())
  })
  
  # 6. Demographic Charts
  output$genderChart <- renderPlotly({
    create_gender_chart(filtered_data())
  })
  
  output$ageChart <- renderPlotly({
    create_age_chart(filtered_data())
  })
  
  # 7. Geographic Visualizations
  output$incidentMap <- renderLeaflet({
    create_incident_map(filtered_data())
  })
  
  output$countryHeatmap <- renderPlotly({
    create_country_heatmap(filtered_data(), 'Country of Origin')
  })
}

# Run the application
shinyApp(ui = ui, server = server)