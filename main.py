import glob
import pandas as pd
import h3
import folium

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

# Get unique H3 indexes
unique_h3 = df['h3_index'].unique()

# Sum fare_amount for each h3 cell
fare_by_cell = df.groupby('h3_index')['fare_amount'].sum()

# Create map centered at mean location
center = [df[lat_col].mean(), df[lng_col].mean()]
m = folium.Map(location=center, zoom_start=10)

# Add H3 hexagons to map with fare sum as popup
for h in unique_h3:
    boundary = h3.cell_to_boundary(h)
    fare_sum = fare_by_cell.get(h, 0)
    folium.Polygon(
        locations=boundary,
        color='blue',
        fill=True,
        fill_opacity=0.2,
        popup=f"Total Fare: ${fare_sum:.2f}"
    ).add_to(m)

# Save map
m.save('h3_index_map.html')
print("Map saved to h3_index_map.html")