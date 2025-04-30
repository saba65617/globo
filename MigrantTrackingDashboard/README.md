# Missing Migrants Analysis Dashboard (2014-2024)

This is an R Shiny dashboard application for analyzing and visualizing the "Global Missing Migrants Dataset". The dashboard explores trends in migrant deaths and disappearances worldwide between 2014 and 2024.

## Features

- Interactive filters for year range, region, and cause of death
- Key statistics showing total incidents, deaths, missing persons, and casualties
- Five visualization tabs:
  - **Yearly Trends**: Charts showing annual and monthly patterns
  - **Regional Analysis**: Visualizations of regions of origin, incident locations, and migration routes
  - **Causes of Death**: Analysis of different causes and how they've changed over time
  - **Demographics**: Gender and age distribution of missing migrants
  - **Geographic Distribution**: Interactive map of incident locations and country-level heatmap

## Requirements

To run this application, you'll need R with the following packages installed:

```r
install.packages(c(
  "shiny",
  "shinydashboard",
  "shinythemes",
  "readr",
  "dplyr",
  "plotly",
  "leaflet",
  "DT",
  "ggplot2",
  "tidyr",
  "RColorBrewer",
  "lubridate",
  "stringr"
))
```

## File Structure

- `app.R`: The main Shiny application file
- `data_processing.R`: Functions for cleaning and processing the dataset
- `visualization.R`: Functions for creating various charts, maps, and visualizations
- `utils.R`: Utility functions for formatting and calculations
- `attached_assets/Global Missing Migrants Dataset.csv`: The dataset

## How to Run

1. Make sure you have R installed on your computer
2. Install the required packages listed above
3. Download all files to a directory
4. Open R or RStudio
5. Set the working directory to the folder containing the files
6. Run the following command:

```r
shiny::runApp()
```

## Dataset Description

The "Global Missing Migrants Dataset" contains information about deceased and missing migrants around the world from 2014 to 2024. It includes:

- Incident details (year, month, location)
- Region and country information
- Casualty counts (dead, missing, survivors)
- Demographic data (gender, age)
- Cause of death
- Migration routes

This dashboard helps visualize this humanitarian data to raise awareness about the challenges and dangers faced by migrants globally.

## Dashboard Design

The dashboard features a dark sidebar with filters and a light-colored main content area with multiple visualization tabs. The design is inspired by modern data visualization dashboards, with emphasis on clean presentation and intuitive interaction.

## Created For

This project was created as a college assignment to demonstrate skills in R data visualization and Shiny application development.