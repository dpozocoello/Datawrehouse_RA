
import json
import unicodedata

def normalize_name(name):
    if not name: return ""
    name = str(name)
    name = unicodedata.normalize('NFD', name)
    name = "".join([c for c in name if unicodedata.category(c) != 'Mn'])
    return name.upper().strip()

# Check Provincias
print("--- PROVINCIAS ---")
with open(r"D:\DashboardRA\Dash_board_RG_v1.01\ecuador_provincias.geojson", encoding='utf-8') as f:
    geo_p = json.load(f)

for i, feature in enumerate(geo_p['features'][:5]):
    props = feature['properties']
    print(f"Feature {i} properties: {props.keys()}")
    for k, v in props.items():
        print(f"  {k}: {v} -> normalized: {normalize_name(v)}")

# Check Cantones
print("\n--- CANTONES ---")
with open(r"D:\DashboardRA\Dash_board_RG_v1.01\ecuador_cantones.geojson", encoding='utf-8') as f:
    geo_c = json.load(f)

for i, feature in enumerate(geo_c['features'][:5]):
    props = feature['properties']
    print(f"Feature {i} properties: {props.keys()}")
    for k, v in props.items():
        if 'canton' in k.lower() or 'name' in k.lower():
            print(f"  {k}: {v} -> normalized: {normalize_name(v)}")
