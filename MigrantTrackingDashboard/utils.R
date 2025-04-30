library(stringr)

# Function to extract numbers from a string
extract_numbers_from_str <- function(s) {
  if (is.na(s)) {
    return(0)
  }
  
  tryCatch({
    if (is.numeric(s)) {
      return(as.numeric(s))
    }
    
    # Extract first number from the string
    matches <- str_extract_all(as.character(s), "[-+]?\\d*\\.?\\d+")[[1]]
    if (length(matches) > 0) {
      return(as.numeric(matches[1]))
    }
    return(0)
  }, error = function(e) {
    return(0)
  })
}

# Function to safely divide two numbers
safe_division <- function(numerator, denominator) {
  tryCatch({
    if (denominator == 0) {
      return(0)
    }
    return(numerator / denominator)
  }, error = function(e) {
    return(0)
  })
}

# Function to format a number with commas
format_number <- function(num, decimal_places = 0) {
  tryCatch({
    if (decimal_places == 0) {
      return(format(as.integer(num), big.mark = ","))
    } else {
      return(format(round(num, decimal_places), big.mark = ",", nsmall = decimal_places))
    }
  }, error = function(e) {
    return("0")
  })
}

# Function to calculate and format percentage
calculate_percentage <- function(part, total) {
  tryCatch({
    if (total == 0) {
      return("0%")
    }
    percentage <- (part / total) * 100
    return(paste0(round(percentage, 1), "%"))
  }, error = function(e) {
    return("0%")
  })
}

# Function to get a color on a gradient based on value
get_color_for_value <- function(value, min_val, max_val, 
                               color_start = c(200, 230, 255), 
                               color_end = c(0, 70, 180)) {
  tryCatch({
    # Handle edge cases
    if (max_val == min_val) {
      ratio <- 0
    } else {
      ratio <- (value - min_val) / (max_val - min_val)
    }
    
    # Ensure ratio is between 0 and 1
    ratio <- max(0, min(1, ratio))
    
    # Calculate color components
    r <- as.integer(color_start[1] + ratio * (color_end[1] - color_start[1]))
    g <- as.integer(color_start[2] + ratio * (color_end[2] - color_start[2]))
    b <- as.integer(color_start[3] + ratio * (color_end[3] - color_start[3]))
    
    # Convert to hex
    return(sprintf("#%02x%02x%02x", r, g, b))
  }, error = function(e) {
    return("#CCCCCC")  # Default gray color in case of error
  })
}