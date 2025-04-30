library(DBI)
library(RPostgres)

# Function to establish a connection to the PostgreSQL database
connect_to_database <- function() {
  # Get database connection parameters from environment variables
  db_host <- Sys.getenv("PGHOST")
  db_port <- Sys.getenv("PGPORT")
  db_name <- Sys.getenv("PGDATABASE")
  db_user <- Sys.getenv("PGUSER")
  db_password <- Sys.getenv("PGPASSWORD")
  
  # Create the connection
  con <- dbConnect(
    RPostgres::Postgres(),
    host = db_host,
    port = db_port,
    dbname = db_name,
    user = db_user,
    password = db_password
  )
  
  return(con)
}

# Function to get incident data from the database
get_incident_data <- function(con, year_from = NULL, year_to = NULL, 
                             region = NULL, cause = NULL) {
  # Start building the query
  query <- "SELECT * FROM incidents"
  
  # Add filters
  conditions <- c()
  
  if (!is.null(year_from) && !is.null(year_to)) {
    conditions <- c(conditions, 
                   sprintf("incident_year BETWEEN %d AND %d", year_from, year_to))
  }
  
  if (!is.null(region) && region != "All Regions") {
    conditions <- c(conditions, 
                   sprintf("region_of_incident = '%s'", gsub("'", "''", region)))
  }
  
  if (!is.null(cause) && cause != "All Causes") {
    conditions <- c(conditions, 
                   sprintf("cause_of_death = '%s'", gsub("'", "''", cause)))
  }
  
  # Combine conditions if any
  if (length(conditions) > 0) {
    query <- paste(query, "WHERE", paste(conditions, collapse = " AND "))
  }
  
  # Execute query
  data <- dbGetQuery(con, query)
  
  return(data)
}

# Function to get countries for each incident
get_countries_for_incidents <- function(con, incident_ids) {
  if (length(incident_ids) == 0) {
    return(data.frame(incident_id = integer(), country_name = character()))
  }
  
  # Format incident IDs for SQL IN clause
  ids_str <- paste(incident_ids, collapse = ",")
  
  query <- sprintf("
    SELECT ic.incident_id, c.country_name
    FROM incident_countries ic
    JOIN countries c ON ic.country_id = c.id
    WHERE ic.incident_id IN (%s)
  ", ids_str)
  
  countries_data <- dbGetQuery(con, query)
  
  return(countries_data)
}

# Function to get all regions
get_all_regions <- function(con) {
  query <- "SELECT DISTINCT region_of_incident FROM incidents WHERE region_of_incident IS NOT NULL"
  regions <- dbGetQuery(con, query)
  return(c("All Regions", sort(regions$region_of_incident)))
}

# Function to get all causes of death
get_all_causes <- function(con) {
  query <- "SELECT DISTINCT cause_of_death FROM incidents WHERE cause_of_death IS NOT NULL"
  causes <- dbGetQuery(con, query)
  return(c("All Causes", sort(causes$cause_of_death)))
}

# Function to get min and max years from the database
get_year_range <- function(con) {
  query <- "SELECT MIN(incident_year) as min_year, MAX(incident_year) as max_year FROM incidents"
  year_range <- dbGetQuery(con, query)
  return(list(min = year_range$min_year, max = year_range$max_year))
}

# Function to close database connection
close_database_connection <- function(con) {
  dbDisconnect(con)
}