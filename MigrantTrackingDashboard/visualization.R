library(ggplot2)
library(plotly)
library(leaflet)
library(RColorBrewer)
library(dplyr)

# Color palette
COLOR_PALETTE <- c('#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', 
                   '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf')

# Function to create a yearly trend chart
create_yearly_trend_chart <- function(data) {
  yearly_data <- get_yearly_data(data)
  
  # Calculate total casualties for each year for hover info
  yearly_data$`Total Casualties` <- yearly_data$`Number of Dead` + yearly_data$`Minimum Estimated Number of Missing`
  
  # Calculate average casualties per incident for hover info
  yearly_data$`Avg Per Incident` <- yearly_data$`Total Casualties` / yearly_data$`Incident Count`
  
  # Modern color palette matching our dashboard theme
  death_color <- "#6366f1"       # Indigo - matching our primary purple
  missing_color <- "#10b981"     # Emerald - complementary to our theme
  incident_color <- "#f43f5e"    # Red-pink - for incidents line
  
  # Create the plot with plotly - modern styling
  p <- plot_ly() %>%
    add_bars(
      data = yearly_data,
      x = ~`Incident year`,
      y = ~`Number of Dead`,
      customdata = ~`Total Casualties`,
      name = "Deaths",
      marker = list(
        color = death_color,
        line = list(color = adjustcolor(death_color, alpha.f = 0.7), width = 0)
      ),
      hovertemplate = paste(
        "<b>%{x}</b><br>",
        "Deaths: <b>%{y:,}</b><br>",
        "Total Casualties: %{customdata:,}<br>",
        "<extra></extra>"
      )
    ) %>%
    add_bars(
      data = yearly_data,
      x = ~`Incident year`,
      y = ~`Minimum Estimated Number of Missing`,
      customdata = ~`Total Casualties`,
      name = "Missing",
      marker = list(
        color = missing_color,
        line = list(color = adjustcolor(missing_color, alpha.f = 0.7), width = 0)
      ),
      hovertemplate = paste(
        "<b>%{x}</b><br>",
        "Missing: <b>%{y:,}</b><br>",
        "Total Casualties: %{customdata:,}<br>",
        "<extra></extra>"
      )
    ) %>%
    add_trace(
      data = yearly_data,
      x = ~`Incident year`,
      y = ~`Incident Count`,
      customdata = ~`Avg Per Incident`,
      name = "Incident Count",
      type = 'scatter',
      mode = 'lines+markers',
      yaxis = 'y2',
      line = list(
        color = incident_color,
        width = 3,
        shape = 'spline',
        smoothing = 0.8
      ),
      marker = list(
        size = 10,
        color = incident_color,
        line = list(color = "white", width = 2)
      ),
      hovertemplate = paste(
        "<b>%{x}</b><br>",
        "Incidents: <b>%{y:,}</b><br>",
        "Avg Casualties per Incident: %{customdata:.1f}<br>",
        "<extra></extra>"
      )
    ) %>%
    layout(
      barmode = 'stack',
      title = list(
        text = 'Yearly Trend of Migrant Deaths and Disappearances',
        font = list(
          family = "Inter, sans-serif",
          size = 18,
          color = "#334155"
        ),
        x = 0.01,
        xanchor = "left"
      ),
      xaxis = list(
        title = list(
          text = 'Year',
          font = list(
            family = "Inter, sans-serif",
            size = 14,
            color = "#64748b"
          )
        ),
        tickmode = 'linear',
        tickfont = list(
          family = "Inter, sans-serif",
          size = 12,
          color = "#64748b"
        ),
        gridcolor = '#f1f5f9',
        zerolinecolor = '#e2e8f0'
      ),
      yaxis = list(
        title = list(
          text = 'Number of Casualties',
          font = list(
            family = "Inter, sans-serif",
            size = 14,
            color = "#64748b"
          )
        ),
        tickfont = list(
          family = "Inter, sans-serif",
          size = 12,
          color = "#64748b"
        ),
        gridcolor = '#f1f5f9',
        zerolinecolor = '#e2e8f0'
      ),
      yaxis2 = list(
        title = list(
          text = 'Number of Incidents',
          font = list(
            family = "Inter, sans-serif",
            size = 14,
            color = "#64748b"
          )
        ),
        tickfont = list(
          family = "Inter, sans-serif",
          size = 12,
          color = "#64748b"
        ),
        overlaying = 'y',
        side = 'right',
        gridcolor = 'transparent',
        zerolinecolor = '#e2e8f0'
      ),
      legend = list(
        orientation = "h",
        xanchor = "center",
        x = 0.5,
        y = 1.1,
        bgcolor = 'rgba(255, 255, 255, 0.8)',
        bordercolor = 'rgba(0, 0, 0, 0.1)',
        borderwidth = 1,
        font = list(
          family = "Inter, sans-serif",
          size = 12,
          color = "#334155"
        )
      ),
      paper_bgcolor = 'rgba(0,0,0,0)',
      plot_bgcolor = 'rgba(0,0,0,0)',
      margin = list(l = 60, r = 60, t = 80, b = 60),
      hoverlabel = list(
        bgcolor = "#334155",
        bordercolor = "#334155",
        font = list(family = "Inter, sans-serif", size = 13, color = "white")
      )
    )
  
  return(p)
}

# Function to create a monthly distribution chart
create_monthly_chart <- function(data) {
  # Get monthly data
  monthly_data <- get_monthly_data(data)
  
  # Create a pivot table for heatmap
  pivot_data <- monthly_data %>%
    select(`Incident year`, `Reported Month`, `Month Number`, `Total Number of Dead and Missing`) %>%
    group_by(`Incident year`, `Reported Month`, `Month Number`) %>%
    summarize(Value = sum(`Total Number of Dead and Missing`, na.rm = TRUE)) %>%
    ungroup()
  
  # Month order
  month_order <- c(
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'
  )
  
  # Convert to factors for proper ordering
  pivot_data$`Reported Month` <- factor(pivot_data$`Reported Month`, levels = month_order)
  
  # Calculate max value for color scaling
  max_value <- max(pivot_data$Value, na.rm = TRUE)
  
  # Custom hover template
  hovertemplate <- paste(
    "<b>%{y} %{x}</b><br>",
    "Casualties: <b>%{z:,}</b><br>",
    "<extra></extra>"
  )
  
  # Modern gradient color palette - blue to purple to red
  custom_colorscale <- list(
    c(0, "#f0f9ff"),            # Very light blue
    c(0.2, "#bae6fd"),          # Light blue
    c(0.4, "#60a5fa"),          # Medium blue
    c(0.6, "#6366f1"),          # Indigo
    c(0.8, "#c084fc"),          # Purple
    c(1.0, "#f43f5e")           # Red
  )
  
  # Create heatmap with modern styling
  p <- plot_ly(
    data = pivot_data,
    x = ~`Incident year`,
    y = ~`Reported Month`,
    z = ~Value,
    type = "heatmap",
    colorscale = custom_colorscale,
    hovertemplate = hovertemplate,
    showscale = TRUE
  ) %>%
    layout(
      title = list(
        text = 'Monthly Distribution of Migrant Deaths and Disappearances',
        font = list(
          family = "Inter, sans-serif",
          size = 18,
          color = "#334155"
        ),
        x = 0.01,
        xanchor = "left"
      ),
      xaxis = list(
        title = list(
          text = 'Year',
          font = list(
            family = "Inter, sans-serif",
            size = 14,
            color = "#64748b"
          )
        ),
        tickfont = list(
          family = "Inter, sans-serif",
          size = 12,
          color = "#64748b"
        ),
        gridcolor = '#f1f5f9'
      ),
      yaxis = list(
        title = list(
          text = 'Month',
          font = list(
            family = "Inter, sans-serif",
            size = 14,
            color = "#64748b"
          )
        ),
        categoryorder = "array", 
        categoryarray = month_order,
        tickfont = list(
          family = "Inter, sans-serif",
          size = 12,
          color = "#64748b"
        ),
        gridcolor = '#f1f5f9'
      ),
      coloraxis = list(
        colorbar = list(
          title = list(
            text = "Number of Casualties",
            font = list(
              family = "Inter, sans-serif",
              size = 12,
              color = "#64748b"
            )
          ),
          tickfont = list(
            family = "Inter, sans-serif",
            size = 10,
            color = "#64748b"
          ),
          thickness = 15,
          len = 0.7,
          outlinewidth = 0,
          bgcolor = 'rgba(255,255,255,0.8)'
        )
      ),
      paper_bgcolor = 'rgba(0,0,0,0)',
      plot_bgcolor = 'rgba(0,0,0,0)',
      margin = list(l = 60, r = 30, t = 80, b = 60),
      hoverlabel = list(
        bgcolor = "#334155",
        bordercolor = "#334155",
        font = list(family = "Inter, sans-serif", size = 13, color = "white")
      ),
      annotations = list(
        list(
          text = "Seasonal patterns in migrant deaths and disappearances",
          x = 0.5,
          y = -0.15,
          xref = "paper",
          yref = "paper",
          showarrow = FALSE,
          font = list(
            family = "Inter, sans-serif",
            size = 12,
            color = "#64748b"
          )
        )
      )
    )
  
  return(p)
}

# Function to create a region chart
create_region_chart <- function(data, region_column) {
  region_data <- get_region_data(data, region_column)
  
  # Get top 10 regions
  top_regions <- head(region_data, 10)
  
  # Convert to factor for proper ordering in plot
  top_regions[[region_column]] <- factor(top_regions[[region_column]], 
                                        levels = rev(top_regions[[region_column]]))
  
  # Calculate percentage of total for each region
  total_casualties <- sum(region_data$`Total Number of Dead and Missing`, na.rm = TRUE)
  top_regions$Percentage <- (top_regions$`Total Number of Dead and Missing` / total_casualties) * 100
  
  # Create custom hover text
  top_regions$hover_text <- paste0(
    "<b>", top_regions[[region_column]], "</b><br>",
    "Casualties: ", format(top_regions$`Total Number of Dead and Missing`, big.mark = ","), "<br>",
    "Incidents: ", format(top_regions$`Incident Count`, big.mark = ","), "<br>",
    "Share of Total: ", format(round(top_regions$Percentage, 1)), "%"
  )
  
  # Modern color gradient
  if (region_column == 'Region of Origin') {
    color_gradient <- list(
      c(0, "#4338ca"),     # Start with indigo (matches our dashboard theme)
      c(1, "#8b5cf6")      # End with purple
    )
  } else {
    color_gradient <- list(
      c(0, "#0891b2"),     # Start with cyan
      c(1, "#06b6d4")      # End with light cyan
    )
  }
  
  # Create horizontal bar chart with modern styling
  p <- plot_ly(
    data = top_regions,
    x = ~`Total Number of Dead and Missing`,
    y = ~get(region_column),
    type = 'bar',
    orientation = 'h',
    text = ~hover_text,
    hoverinfo = 'text',
    marker = list(
      color = ~`Total Number of Dead and Missing`,
      colorscale = color_gradient,
      line = list(color = 'rgba(255,255,255,0.5)', width = 1)
    ),
    texttemplate = '%{x:,}',
    textposition = 'outside',
    textfont = list(
      family = "Inter, sans-serif",
      size = 12,
      color = "#334155"
    )
  ) %>%
    layout(
      title = list(
        text = if (region_column == 'Region of Origin') 
               'Top Regions of Origin by Casualties' 
               else 'Top Regions where Incidents Occurred',
        font = list(
          family = "Inter, sans-serif",
          size = 18,
          color = "#334155"
        ),
        x = 0.01,
        xanchor = "left"
      ),
      xaxis = list(
        title = list(
          text = 'Number of Casualties',
          font = list(
            family = "Inter, sans-serif",
            size = 14,
            color = "#64748b"
          )
        ),
        tickfont = list(
          family = "Inter, sans-serif",
          size = 12,
          color = "#64748b"
        ),
        gridcolor = '#f1f5f9',
        zerolinecolor = '#e2e8f0'
      ),
      yaxis = list(
        title = '',
        tickfont = list(
          family = "Inter, sans-serif",
          size = 12,
          color = "#334155"
        ),
        gridcolor = 'rgba(0,0,0,0)'
      ),
      paper_bgcolor = 'rgba(0,0,0,0)',
      plot_bgcolor = 'rgba(0,0,0,0)',
      margin = list(l = 120, r = 30, t = 80, b = 60),
      hoverlabel = list(
        bgcolor = "#334155",
        bordercolor = "#334155",
        font = list(family = "Inter, sans-serif", size = 13, color = "white")
      ),
      bargap = 0.2,
      uniformtext = list(minsize = 10, mode = 'hide'),
      annotations = list(
        list(
          text = paste("Based on data from", min(data$`Incident year`), "to", max(data$`Incident year`)),
          x = 0.5,
          y = -0.15,
          xref = "paper",
          yref = "paper",
          showarrow = FALSE,
          font = list(
            family = "Inter, sans-serif",
            size = 12,
            color = "#64748b"
          )
        )
      )
    )
  
  return(p)
}

# Function to create a cause of death chart
create_cause_chart <- function(data) {
  cause_data <- get_cause_data(data)
  
  p <- plot_ly(
    data = cause_data,
    labels = ~`Cause of Death`,
    values = ~`Total Number of Dead and Missing`,
    type = 'pie',
    hole = 0.4,
    marker = list(colors = COLOR_PALETTE),
    textinfo = 'percent+label',
    hoverinfo = 'label+value+percent'
  ) %>%
    layout(
      title = list(text = 'Causes of Death'),
      legend = list(
        orientation = 'h',
        y = -0.2,
        yanchor = 'bottom',
        x = 0.5,
        xanchor = 'center'
      )
    )
  
  return(p)
}

# Function to create a causes of death by year chart
create_cause_year_chart <- function(data) {
  # Group data by year and cause of death
  yearly_cause_data <- data %>%
    group_by(`Incident year`, `Cause of Death`) %>%
    summarize(`Total Number of Dead and Missing` = sum(`Total Number of Dead and Missing`, na.rm = TRUE)) %>%
    ungroup()
  
  p <- plot_ly(
    data = yearly_cause_data,
    x = ~`Incident year`,
    y = ~`Total Number of Dead and Missing`,
    color = ~`Cause of Death`,
    type = 'scatter',
    mode = 'lines',
    fill = 'tonexty',
    line = list(shape = 'spline')
  ) %>%
    layout(
      title = list(text = 'Causes of Death by Year'),
      xaxis = list(title = 'Year'),
      yaxis = list(title = 'Number of Dead and Missing'),
      legend = list(title = list(text = 'Cause of Death'))
    )
  
  return(p)
}

# Function to create a migration route chart
create_route_chart <- function(data) {
  route_data <- get_route_data(data)
  
  # Convert to factor for proper ordering in plot
  route_data$`Migration route` <- factor(route_data$`Migration route`, 
                                        levels = rev(route_data$`Migration route`))
  
  p <- plot_ly(
    data = route_data,
    x = ~`Total Number of Dead and Missing`,
    y = ~`Migration route`,
    type = 'bar',
    orientation = 'h',
    marker = list(
      color = ~`Total Number of Dead and Missing`,
      colorscale = 'Viridis'
    ),
    text = ~`Total Number of Dead and Missing`,
    textposition = 'outside',
    texttemplate = '%{text:,}'
  ) %>%
    layout(
      title = list(text = 'Top Migration Routes by Number of Dead and Missing'),
      xaxis = list(title = 'Number of Dead and Missing'),
      yaxis = list(title = ''),
      height = 700
    )
  
  return(p)
}

# Function to create a gender distribution chart
create_gender_chart <- function(data) {
  demographic_data <- get_demographic_data(data)
  gender_data <- demographic_data$gender
  
  color_map <- c(
    'Female' = '#FF9AA2',
    'Male' = '#A2D2FF',
    'Children' = '#BAFFC9',
    'Unknown' = '#E2E2E2'
  )
  
  p <- plot_ly(
    data = gender_data,
    labels = ~Gender,
    values = ~Count,
    type = 'pie',
    marker = list(colors = color_map[gender_data$Gender]),
    textinfo = 'percent+label',
    hoverinfo = 'label+value+percent'
  ) %>%
    layout(
      title = list(text = 'Gender Distribution')
    )
  
  return(p)
}

# Function to create an age group distribution chart
create_age_chart <- function(data) {
  demographic_data <- get_demographic_data(data)
  age_data <- demographic_data$age
  
  color_map <- c(
    'Children (<18)' = '#BAFFC9',
    'Adults (18+)' = '#A2D2FF',
    'Unknown' = '#E2E2E2'
  )
  
  p <- plot_ly(
    data = age_data,
    labels = ~`Age Group`,
    values = ~Count,
    type = 'pie',
    marker = list(colors = color_map[age_data$`Age Group`]),
    textinfo = 'percent+label',
    hoverinfo = 'label+value+percent'
  ) %>%
    layout(
      title = list(text = 'Age Group Distribution')
    )
  
  return(p)
}

# Function to create an incident map
create_incident_map <- function(data) {
  # Filter data with valid coordinates
  map_data <- data %>%
    filter(!is.na(Latitude) & !is.na(Longitude))
  
  # Create a color palette based on cause of death
  causes <- unique(map_data$`Cause of Death`)
  pal <- colorFactor(
    palette = colorRampPalette(c("#4338ca", "#6366f1", "#818cf8", "#22d3ee", "#ec4899", "#f43f5e", "#f97316"))(length(causes)),
    domain = causes
  )
  
  # Custom icon HTML for better visual appearance
  makeCustomIcon <- function(casualties) {
    size <- pmin(pmax(20, sqrt(casualties) * 2), 45) # Size based on casualties with min and max
    
    # Color based on size
    if (casualties < 10) {
      color <- "#4338ca" # Indigo
    } else if (casualties < 50) {
      color <- "#6366f1" # Light indigo
    } else if (casualties < 100) {
      color <- "#ec4899" # Pink
    } else {
      color <- "#f43f5e" # Red
    }
    
    # Create a pulsing circle with the number inside
    return(sprintf("
      <div style='
        background-color: %s;
        width: %dpx;
        height: %dpx;
        border-radius: 50%%;
        color: white;
        font-weight: bold;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: %dpx;
        box-shadow: 0 0 0 rgba(66, 153, 225, 0.6);
        animation: pulse 2s infinite;
      '>%d</div>
      <style>
        @keyframes pulse {
          0%% {
            box-shadow: 0 0 0 0 rgba(66, 153, 225, 0.7);
          }
          70%% {
            box-shadow: 0 0 0 10px rgba(66, 153, 225, 0);
          }
          100%% {
            box-shadow: 0 0 0 0 rgba(66, 153, 225, 0);
          }
        }
      </style>
    ", color, size, size, size/3, casualties))
  }
  
  # Custom popup styling
  createPopupContent <- function(data) {
    cause_color <- pal(data$`Cause of Death`)
    
    paste0("<div style='font-family: Inter, sans-serif; width: 250px;'>",
          "<h3 style='margin-top: 0; color: #334155; border-bottom: 2px solid ", cause_color, "; padding-bottom: 8px;'>", 
          "Incident Details</h3>",
          "<div style='margin: 5px 0;'><span style='color: #64748b; font-weight: 500;'>Date: </span>", 
          "<span style='color: #334155;'>", data$`Reported Month`, " ", as.integer(data$`Incident year`), "</span></div>",
          "<div style='margin: 5px 0;'><span style='color: #64748b; font-weight: 500;'>Location: </span>", 
          "<span style='color: #334155;'>", data$`Region of Incident`, "</span></div>",
          "<div style='margin: 5px 0;'><span style='color: #64748b; font-weight: 500;'>Casualties: </span>", 
          "<span style='color: #ef4444; font-weight: 600;'>", as.integer(data$`Total Number of Dead and Missing`), "</span></div>",
          "<div style='margin: 5px 0;'><span style='color: #64748b; font-weight: 500;'>Cause: </span>", 
          "<span style='color: ", cause_color, ";'>", data$`Cause of Death`, "</span></div>",
          "<div style='margin: 5px 0;'><span style='color: #64748b; font-weight: 500;'>Route: </span>", 
          "<span style='color: #334155;'>", data$`Migration route`, "</span></div>",
          "</div>")
  }
  
  # Create leaflet map with modern styling
  m <- leaflet(map_data, options = leafletOptions(minZoom = 2)) %>%
    addProviderTiles("CartoDB.Voyager", options = providerTileOptions(
      attribution = 'Map data © <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors | 
                     Tiles © <a href="https://carto.com/attribution/">CARTO</a>'
    )) %>%
    setView(lng = 0, lat = 20, zoom = 2) %>%
    addScaleBar(position = "bottomleft", options = scaleBarOptions(imperial = FALSE)) %>%
    addEasyButton(easyButton(
      icon = "fa-home", title = "Reset View",
      onClick = JS("function(btn, map){ map.setView([20, 0], 2); }")
    ))
  
  # Add a heatmap layer for density visualization
  m <- m %>%
    addHeatmap(
      lng = ~Longitude, 
      lat = ~Latitude, 
      intensity = ~`Total Number of Dead and Missing`,
      blur = 25, 
      max = max(map_data$`Total Number of Dead and Missing`, na.rm = TRUE) * 0.5,
      radius = 15,
      gradient = c("#eff6ff", "#93c5fd", "#3b82f6", "#1d4ed8", "#f87171", "#ef4444", "#b91c1c")
    )
  
  # Add clustered markers with custom HTML icons
  m <- m %>%
    addMarkers(
      ~Longitude, ~Latitude,
      icon = ~makeIcon(
        html = makeCustomIcon(`Total Number of Dead and Missing`),
        iconAnchorX = 15, iconAnchorY = 15
      ),
      popup = ~createPopupContent(.),
      clusterOptions = markerClusterOptions(
        iconCreateFunction = JS("
          function(cluster) {
            var childCount = cluster.getChildCount();
            var size = Math.min(Math.max(30, childCount * 0.5), 60);
            
            var color;
            if (childCount < 50) {
              color = '#6366f1';
            } else if (childCount < 100) {
              color = '#8b5cf6';
            } else {
              color = '#f43f5e';
            }
            
            return L.divIcon({
              html: '<div style=\"background-color: ' + color + '; width: ' + size + 'px; height: ' + size + 'px; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold; font-size: ' + (size/3) + 'px;\">' + childCount + '</div>',
              className: 'marker-cluster',
              iconSize: L.point(size, size)
            });
          }
        "),
        spiderfyOnMaxZoom = TRUE,
        showCoverageOnHover = FALSE,
        zoomToBoundsOnClick = TRUE,
        maxClusterRadius = 40
      )
    )
    
  # Add legend for cause of death
  m <- m %>%
    addLegend(
      position = "bottomright",
      pal = pal,
      values = ~`Cause of Death`,
      title = "Cause of Death",
      opacity = 0.8,
      labels = causes
    )
  
  return(m)
}

# Function to create a country heatmap
create_country_heatmap <- function(data, country_column) {
  # Handle countries lists
  if (country_column == 'Country of Origin' && 'Countries List' %in% colnames(data)) {
    # Process countries list
    country_data <- data %>%
      group_by(`Country of Origin`) %>%
      summarize(
        `Total Number of Dead and Missing` = sum(`Total Number of Dead and Missing`, na.rm = TRUE),
        `Incident Count` = n(),
        `Average Per Incident` = mean(`Total Number of Dead and Missing`, na.rm = TRUE)
      ) %>%
      ungroup() %>%
      arrange(desc(`Total Number of Dead and Missing`))
    
    country_data <- rename(country_data, Country = `Country of Origin`)
  } else {
    # Process single country column
    country_data <- data %>%
      group_by(!!sym(country_column)) %>%
      summarize(
        `Total Number of Dead and Missing` = sum(`Total Number of Dead and Missing`, na.rm = TRUE),
        `Incident Count` = n(),
        `Average Per Incident` = mean(`Total Number of Dead and Missing`, na.rm = TRUE)
      ) %>%
      ungroup() %>%
      arrange(desc(`Total Number of Dead and Missing`))
    
    country_data <- rename(country_data, Country = !!sym(country_column))
  }
  
  # Calculate percentages for hover text
  total_casualties <- sum(country_data$`Total Number of Dead and Missing`, na.rm = TRUE)
  country_data$Percentage <- (country_data$`Total Number of Dead and Missing` / total_casualties) * 100
  
  # Get top 30 countries
  top_countries <- head(country_data, 30)
  
  # Create hover text with multiple metrics
  top_countries$hover_text <- paste0(
    "<b>", top_countries$Country, "</b><br>",
    "Total Casualties: ", format(top_countries$`Total Number of Dead and Missing`, big.mark = ","), "<br>",
    "Incidents: ", format(top_countries$`Incident Count`, big.mark = ","), "<br>",
    "Avg per Incident: ", round(top_countries$`Average Per Incident`, 1), "<br>",
    "Share of Total: ", format(round(top_countries$Percentage, 1)), "%"
  )
  
  # Modern color palette for choropleth map - blue to purple to red gradient
  color_scale <- list(
    c(0, "#4338ca"),      # Dark blue-purple
    c(0.25, "#6366f1"),   # Indigo
    c(0.5, "#a855f7"),    # Purple
    c(0.75, "#ec4899"),   # Pink
    c(1, "#f43f5e")       # Red
  )
  
  # Create choropleth map with modern styling
  p <- plot_ly(
    data = top_countries,
    type = 'choropleth',
    locations = ~Country,
    locationmode = 'country names',
    z = ~`Total Number of Dead and Missing`,
    text = ~hover_text,
    hoverinfo = 'text',
    colorscale = color_scale,
    marker = list(
      line = list(color = 'rgb(240,240,240)', width = 0.5)
    ),
    colorbar = list(
      title = "Casualties",
      thickness = 20,
      len = 0.7,
      bgcolor = 'rgba(255,255,255,0.8)',
      outlinewidth = 0
    )
  ) %>%
    layout(
      title = list(
        text = 'Countries of Origin - Casualty Distribution',
        font = list(
          family = "Inter, sans-serif",
          size = 22,
          color = "#334155"
        ),
        y = 0.95
      ),
      paper_bgcolor = 'rgba(0,0,0,0)',
      plot_bgcolor = 'rgba(0,0,0,0)',
      margin = list(l = 0, r = 0, t = 65, b = 0),
      geo = list(
        showframe = FALSE,
        showcoastlines = TRUE,
        projection = list(type = 'natural earth'),
        showcountries = TRUE,
        countrycolor = 'rgb(240,240,240)',
        showland = TRUE,
        landcolor = 'rgb(250,250,250)',
        showocean = TRUE,
        oceancolor = 'rgb(245,250,255)',
        showlakes = TRUE,
        lakecolor = 'rgb(240,245,255)',
        bgcolor = 'rgba(0,0,0,0)'
      ),
      hoverlabel = list(
        bgcolor = "#334155",
        bordercolor = "#334155",
        font = list(family = "Inter, sans-serif", size = 13, color = "white")
      )
    )
  
  return(p)
}