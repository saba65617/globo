library(dplyr)
library(tidyr)
library(lubridate)
library(stringr)

# Function to clean and preprocess the Missing Migrants dataset
clean_data <- function(df) {
  # Create a copy of the dataframe
  cleaned_df <- df
  
  # Convert year to numeric
  cleaned_df$`Incident year` <- as.numeric(cleaned_df$`Incident year`)
  
  # Extract month number from 'Reported Month'
  month_mapping <- c(
    'January' = 1, 'February' = 2, 'March' = 3, 'April' = 4, 'May' = 5, 'June' = 6,
    'July' = 7, 'August' = 8, 'September' = 9, 'October' = 10, 'November' = 11, 'December' = 12
  )
  cleaned_df$`Month Number` <- month_mapping[cleaned_df$`Reported Month`]
  
  # Fill missing values in numeric columns
  numeric_cols <- c(
    'Number of Dead', 'Minimum Estimated Number of Missing', 
    'Total Number of Dead and Missing', 'Number of Survivors',
    'Number of Females', 'Number of Males', 'Number of Children'
  )
  
  for (col in numeric_cols) {
    cleaned_df[[col]] <- as.numeric(cleaned_df[[col]])
    cleaned_df[[col]][is.na(cleaned_df[[col]])] <- 0
  }
  
  # Extract coordinates for mapping
  cleaned_df$Coordinates <- as.character(cleaned_df$Coordinates)
  
  # Function to extract coordinates
  extract_coordinates <- function(coord_str) {
    if (is.na(coord_str) || coord_str == "nan") {
      return(list(lat = NA, lon = NA))
    }
    
    # Remove any extra spaces and split by comma
    parts <- strsplit(gsub(" ", "", coord_str), ",")[[1]]
    
    if (length(parts) >= 2) {
      lat <- as.numeric(parts[1])
      lon <- as.numeric(parts[2])
      return(list(lat = lat, lon = lon))
    } else {
      return(list(lat = NA, lon = NA))
    }
  }
  
  # Apply the function to extract coordinates
  coordinates <- lapply(cleaned_df$Coordinates, extract_coordinates)
  cleaned_df$Latitude <- sapply(coordinates, function(x) x$lat)
  cleaned_df$Longitude <- sapply(coordinates, function(x) x$lon)
  
  # Clean region fields
  region_columns <- c('Region of Origin', 'Region of Incident')
  for (col in region_columns) {
    # Fill missing values with 'Unknown'
    cleaned_df[[col]][is.na(cleaned_df[[col]])] <- 'Unknown'
    
    # Clean up values with special characters or annotations
    cleaned_df[[col]] <- gsub(" \\(P\\)", "", cleaned_df[[col]], fixed = TRUE)
  }
  
  # Clean country of origin
  cleaned_df$`Country of Origin`[is.na(cleaned_df$`Country of Origin`)] <- 'Unknown'
  
  # Process countries with multiple entries
  split_countries <- function(country_str) {
    if (is.na(country_str) || country_str == 'Unknown') {
      return(list('Unknown'))
    }
    
    # Split by comma
    if (grepl(",", country_str)) {
      return(strsplit(country_str, ",\\s*")[[1]])
    }
    return(list(country_str))
  }
  
  # Create a list of countries for each entry
  cleaned_df$`Countries List` <- lapply(cleaned_df$`Country of Origin`, split_countries)
  
  # Clean cause of death
  cleaned_df$`Cause of Death`[is.na(cleaned_df$`Cause of Death`)] <- 'Unknown'
  
  # Clean migration route
  cleaned_df$`Migration route`[is.na(cleaned_df$`Migration route`)] <- 'Unknown route'
  
  # Add a datetime column for time-based analysis
  cleaned_df$Date <- as.Date(paste(
    cleaned_df$`Incident year`, 
    cleaned_df$`Month Number`, 
    "01", 
    sep = "-"
  ))
  
  return(cleaned_df)
}

# Function to aggregate data by year
get_yearly_data <- function(df) {
  yearly_data <- df %>%
    group_by(`Incident year`) %>%
    summarize(
      `Total Number of Dead and Missing` = sum(`Total Number of Dead and Missing`, na.rm = TRUE),
      `Number of Dead` = sum(`Number of Dead`, na.rm = TRUE),
      `Minimum Estimated Number of Missing` = sum(`Minimum Estimated Number of Missing`, na.rm = TRUE),
      `Incident Count` = n()
    ) %>%
    ungroup()
  
  return(yearly_data)
}

# Function to aggregate data by month
get_monthly_data <- function(df) {
  monthly_data <- df %>%
    group_by(`Incident year`, `Month Number`, `Reported Month`) %>%
    summarize(
      `Total Number of Dead and Missing` = sum(`Total Number of Dead and Missing`, na.rm = TRUE),
      `Incident Count` = n()
    ) %>%
    ungroup()
  
  return(monthly_data)
}

# Function to aggregate data by region
get_region_data <- function(df, region_column) {
  region_data <- df %>%
    group_by(.data[[region_column]]) %>%
    summarize(
      `Total Number of Dead and Missing` = sum(`Total Number of Dead and Missing`, na.rm = TRUE),
      `Incident Count` = n()
    ) %>%
    ungroup() %>%
    arrange(desc(`Total Number of Dead and Missing`))
  
  return(region_data)
}

# Function to aggregate data by cause of death
get_cause_data <- function(df) {
  cause_data <- df %>%
    group_by(`Cause of Death`) %>%
    summarize(
      `Total Number of Dead and Missing` = sum(`Total Number of Dead and Missing`, na.rm = TRUE),
      `Incident Count` = n()
    ) %>%
    ungroup() %>%
    arrange(desc(`Total Number of Dead and Missing`))
  
  return(cause_data)
}

# Function to aggregate data by migration route
get_route_data <- function(df) {
  # Filter out unknown routes
  route_df <- df %>% filter(`Migration route` != 'Unknown route')
  
  route_data <- route_df %>%
    group_by(`Migration route`) %>%
    summarize(
      `Total Number of Dead and Missing` = sum(`Total Number of Dead and Missing`, na.rm = TRUE),
      `Incident Count` = n()
    ) %>%
    ungroup() %>%
    arrange(desc(`Total Number of Dead and Missing`)) %>%
    head(15)  # Get only top 15 routes
  
  return(route_data)
}

# Function to prepare demographic data for gender and age analysis
get_demographic_data <- function(df) {
  # Sum up the gender counts
  total_females <- sum(df$`Number of Females`, na.rm = TRUE)
  total_males <- sum(df$`Number of Males`, na.rm = TRUE)
  total_children <- sum(df$`Number of Children`, na.rm = TRUE)
  total_unknown <- sum(df$`Total Number of Dead and Missing`, na.rm = TRUE) - 
                  (total_females + total_males + total_children)
  
  # Create gender dataframe
  gender_data <- data.frame(
    Gender = c('Female', 'Male', 'Children', 'Unknown'),
    Count = c(total_females, total_males, total_children, total_unknown)
  )
  
  # Create age dataframe (assuming children are under 18)
  age_data <- data.frame(
    `Age Group` = c('Children (<18)', 'Adults (18+)', 'Unknown'),
    Count = c(
      total_children,
      total_males + total_females,
      total_unknown
    )
  )
  
  return(list(
    gender = gender_data,
    age = age_data
  ))
}