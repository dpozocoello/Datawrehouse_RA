import json

def check_keys(path, name_key):
    print(f"--- Checking {path} ---")
    with open(path, encoding='utf-8') as f:
        data = json.load(f)
        for i in range(min(5, len(data['features']))):
            props = data['features'][i]['properties']
            print(f"Feature {i}: {props.get(name_key, 'MISSING')} | Keys: {list(props.keys())}")

check_keys("d:/DashboardRA/ecuador_provincias.geojson", "name")
check_keys("d:/DashboardRA/ecuador_cantones.geojson", "name")
check_keys("d:/DashboardRA/ecuador_cantones.geojson", "canton")
