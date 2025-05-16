import h3
import requests
import time
import json

# List of H3 cell indexes to process (replace with your list or load from your data)
h3_cells = [
    '872a10011ffffff', '872a10012ffffff', '872a10042ffffff', '872a1006dffffff', '872a10080ffffff',
    '872a10086ffffff', '872a10088ffffff', '872a10089ffffff', '872a1008affffff', '872a1008bffffff',
    '872a1008cffffff', '872a1008dffffff', '872a100a8ffffff', '872a100a9ffffff', '872a100aaffffff',
    '872a100abffffff', '872a100aeffffff', '872a100c0ffffff', '872a100c1ffffff', '872a100c3ffffff',
    '872a100c4ffffff', '872a100c5ffffff', '872a100c6ffffff', '872a100c8ffffff', '872a100cdffffff',
    '872a100d0ffffff', '872a100d1ffffff', '872a100d2ffffff', '872a100d3ffffff', '872a100d4ffffff',
    '872a100d5ffffff', '872a100d6ffffff', '872a100d8ffffff', '872a100d9ffffff', '872a100daffffff',
    '872a100dbffffff', '872a100dcffffff', '872a100ddffffff', '872a100deffffff', '872a100e0ffffff',
    '872a100e2ffffff', '872a100e3ffffff', '872a100e8ffffff', '872a100eaffffff', '872a100ebffffff',
    '872a100f0ffffff', '872a100f1ffffff', '872a100f2ffffff', '872a100f3ffffff', '872a100f5ffffff',
    '872a100f6ffffff', '872a1015bffffff', '872a10185ffffff', '872a103a4ffffff', '872a103b0ffffff',
    '872a103b1ffffff', '872a103b2ffffff', '872a103b3ffffff', '872a103b4ffffff', '872a103b6ffffff',
    '872a1071affffff', '872a10720ffffff', '872a10721ffffff', '872a10725ffffff', '872a10726ffffff',
    '872a10728ffffff', '872a10729ffffff', '872a1072cffffff', '872a1072dffffff', '872a10745ffffff',
    '872a10746ffffff', '872a10754ffffff', '872a10763ffffff', '872a10764ffffff', '872a10770ffffff',
    '872a10771ffffff', '872a10774ffffff', '872a10775ffffff', '872a10776ffffff', '872a107adffffff',
    '872a1088bffffff', '87754e64dffffff'
]

cell_name_cache = {}
def get_cell_name(cell):
    if cell in cell_name_cache:
        return cell_name_cache[cell]
    lat, lng = h3.cell_to_latlng(cell)
    url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lng}&zoom=16&addressdetails=1"
    headers = {'User-Agent': 'uber-geospatial-indexing-charts/1.0'}
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            display_name = data.get('display_name', 'Unknown')
            # Only use the first two parts of the address
            parts = display_name.split(',')
            name = ', '.join([p.strip() for p in parts[:2]]) if len(parts) >= 2 else display_name
        else:
            name = 'Unknown'
    except Exception:
        name = 'Unknown'
    cell_name_cache[cell] = name
    time.sleep(1)  # Be polite to the API
    return name

# Main logic to collect names for all cells
cell_names = {}
for cell in h3_cells:
    cell_names[cell] = get_cell_name(cell)

# Write results to a JSON file
with open('h3_cell_names.json', 'w') as f:
    json.dump(cell_names, f, indent=2)

print('Cell names written to h3_cell_names.json')
