import plotly.express as px
import pandas as pd

# Create some sample data
df = pd.DataFrame({
    'x': [1, 2, 3, 4],
    'y': [10, 11, 12, 13]
})

# Create a simple plot
fig = px.line(df, x='x', y='y')
print("Plotly is working!") 