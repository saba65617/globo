import numpy as np
import pandas as pd
import re

def extract_numbers_from_str(s):
    """Extract numbers from a string"""
    if pd.isna(s):
        return 0
    
    try:
        if isinstance(s, (int, float)):
            return float(s)
        
        # Extract first number from the string
        matches = re.findall(r"[-+]?\d*\.\d+|\d+", str(s))
        if matches:
            return float(matches[0])
        return 0
    except:
        return 0

def safe_division(numerator, denominator):
    """Safely divide two numbers, avoiding division by zero"""
    try:
        if denominator == 0:
            return 0
        return numerator / denominator
    except:
        return 0

def format_number(num, decimal_places=0):
    """Format a number with commas as thousands separators"""
    try:
        if decimal_places == 0:
            return f"{int(num):,}"
        else:
            return f"{num:,.{decimal_places}f}"
    except:
        return "0"

def calculate_percentage(part, total):
    """Calculate percentage and format it"""
    try:
        if total == 0:
            return "0%"
        percentage = (part / total) * 100
        return f"{percentage:.1f}%"
    except:
        return "0%"

def get_color_for_value(value, min_val, max_val, color_start=(200, 230, 255), color_end=(0, 70, 180)):
    """
    Get a color on a gradient based on a value's position between min and max
    
    Parameters:
    -----------
    value : float
        The value to determine color for
    min_val : float
        The minimum value in the range
    max_val : float
        The maximum value in the range
    color_start : tuple
        RGB tuple for the color at minimum value
    color_end : tuple
        RGB tuple for the color at maximum value
    
    Returns:
    --------
    str
        Hex color code
    """
    try:
        # Handle edge cases
        if max_val == min_val:
            ratio = 0
        else:
            ratio = (value - min_val) / (max_val - min_val)
        
        # Ensure ratio is between 0 and 1
        ratio = max(0, min(1, ratio))
        
        # Calculate color components
        r = int(color_start[0] + ratio * (color_end[0] - color_start[0]))
        g = int(color_start[1] + ratio * (color_end[1] - color_start[1]))
        b = int(color_start[2] + ratio * (color_end[2] - color_start[2]))
        
        # Convert to hex
        return f"#{r:02x}{g:02x}{b:02x}"
    except:
        return "#CCCCCC"  # Default gray color in case of error
