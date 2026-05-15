import json

def check_keys(path):
    print(f"Checking {path}...")
    with open(path, encoding='utf-8') as f:
        data = json.load(f)
        if 'features' in data and len(data['features']) > 0:
            print(f"Keys: {list(data['features'][0]['properties'].keys())}")
            print(f"Sample name value: {data['features'][0]['properties'].get('name', 'N/A')}")
            print(f"Sample DEMA value: {data['features'][0]['properties'].get('DPA_DESPRO', 'N/A')}")
        else:
            print("No features found.")

check_keys("d:/DashboardRA/ecuador_provincias.geojson")
check_keys("d:/DashboardRA/ecuador_cantones.geojson")
