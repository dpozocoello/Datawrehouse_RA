import json

with open("d:/DashboardRA/ecuador_provincias.geojson", encoding='utf-8') as f:
    geo = json.load(f)

print("KEYS:", list(geo['features'][0]['properties'].keys()))
for feat in geo['features']:
    p = feat['properties']
    # Just print the province-like value
    for k, v in p.items():
        if k != 'country':
            print(f"  {k}={v}")
    print("---")
