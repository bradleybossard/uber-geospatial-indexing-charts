import glob
import pandas as pd
import h3
import folium
import colorsys
import matplotlib.pyplot as plt
import os
from matplotlib.backends.backend_pdf import PdfPages
import requests
import time
import json

# Parameters
csv_folder = './csv_data'  # Folder containing CSV files
lat_col = 'pickup_latitude'
lng_col = 'pickup_longitude'
h3_resolution = 7

# Ingest all CSV files
all_files = glob.glob(f"{csv_folder}/*.csv")
df_list = [pd.read_csv(f) for f in all_files]
df = pd.concat(df_list, ignore_index=True)

# Index with H3
df['h3_index'] = df.apply(lambda row: h3.latlng_to_cell(row[lat_col], row[lng_col], h3_resolution), axis=1)

# Convert pickup_datetime to datetime and extract month
if not pd.api.types.is_datetime64_any_dtype(df['pickup_datetime']):
    df['pickup_datetime'] = pd.to_datetime(df['pickup_datetime'])
df['pickup_month'] = df['pickup_datetime'].dt.to_period('M')

# Create map centered at mean location
center = [df[lat_col].mean(), df[lng_col].mean()]
m = folium.Map(location=center, zoom_start=10)

# Generate a color for each month
months = sorted(df['pickup_month'].unique())
num_months = len(months)
color_map = {}
for i, month in enumerate(months):
    # Use HSV to generate distinct colors
    hue = i / max(1, num_months)
    rgb = colorsys.hsv_to_rgb(hue, 0.7, 0.8)
    color = '#%02x%02x%02x' % (int(rgb[0]*255), int(rgb[1]*255), int(rgb[2]*255))
    color_map[month] = color

# Function to get a human-readable name for a cell using precomputed JSON
with open('h3_cell_names.json', 'r') as f:
    cell_name_cache = json.load(f)
def get_cell_name(cell):
    return cell_name_cache.get(cell, 'Unknown')

# Create a FeatureGroup for each month
for month in months:
    layer = folium.FeatureGroup(name=str(month))
    month_df = df[df['pickup_month'] == month]
    fare_by_cell = month_df.groupby('h3_index')['fare_amount'].sum()
    for h in fare_by_cell.index:
        boundary = h3.cell_to_boundary(h)
        fare_sum = fare_by_cell[h]
        cell_name = get_cell_name(h)
        popup_text = f"Month: {month}<br>Hex ID: {h}<br>Area: {cell_name}<br>Total Fare: ${fare_sum:.2f}"
        folium.Polygon(
            locations=boundary,
            color=color_map[month],
            fill=True,
            fill_opacity=0.2,
            popup=popup_text
        ).add_to(layer)
    layer.add_to(m)

# Add layer control to map
folium.LayerControl().add_to(m)

# Save map
m.save('h3_index_map.html')
print("Map saved to h3_index_map.html")

# Create output
#  directory for plots
plot_dir = 'cell_barplots'
os.makedirs(plot_dir, exist_ok=True)

# Create a PDF to save all plots
with PdfPages('cell_revenue_vs_month.pdf') as pdf:
    # For each unique H3 cell, plot revenue vs month
    for h in df['h3_index'].unique():
        cell_df = df[df['h3_index'] == h]
        # Group by month and sum fares
        revenue_by_month = cell_df.groupby('pickup_month')['fare_amount'].sum().sort_index()
        plt.figure(figsize=(8, 4))
        revenue_by_month.plot(kind='bar', color='skyblue')
        cell_name = get_cell_name(h)
        plt.title(f'{cell_name} ({h})')
        plt.xlabel('Month')
        plt.ylabel('Total Fare')
        plt.tight_layout()
        plt.savefig(os.path.join(plot_dir, f'cell_{h}_revenue_vs_month.png'))
        pdf.savefig()  # Save the current figure into the PDF
        plt.close()

print("Plots saved to cell_revenue_vs_month.pdf")