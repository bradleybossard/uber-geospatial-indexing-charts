import glob
import pandas as pd
import h3
import folium
import colorsys

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

# Create a FeatureGroup for each month
for month in months:
    layer = folium.FeatureGroup(name=str(month))
    month_df = df[df['pickup_month'] == month]
    fare_by_cell = month_df.groupby('h3_index')['fare_amount'].sum()
    for h in fare_by_cell.index:
        boundary = h3.cell_to_boundary(h)
        fare_sum = fare_by_cell[h]
        folium.Polygon(
            locations=boundary,
            color=color_map[month],
            fill=True,
            fill_opacity=0.2,
            popup=f"Total Fare: ${fare_sum:.2f}"
        ).add_to(layer)
    layer.add_to(m)

# Add layer control to map
folium.LayerControl().add_to(m)

# # Inject custom JS for 'Hide All Layers' button
# hide_layers_js = '''
# <script>
# function hideAllLayers() {
#     var overlays = document.querySelectorAll('.leaflet-control-layers-overlays input[type=checkbox]');
#     overlays.forEach(function(cb) { if(cb.checked) cb.click(); });
# }
# var btn = document.createElement('button');
# btn.innerHTML = 'Hide All Layers';
# btn.style.position = 'absolute';
# btn.style.top = '10px';
# btn.style.right = '10px';
# btn.style.zIndex = 1000;
# btn.onclick = hideAllLayers;
# document.body.appendChild(btn);
# </script>
# '''

# m.get_root().html.add_child(folium.Element(hide_layers_js))

# Save map
m.save('h3_index_map.html')
print("Map saved to h3_index_map.html")