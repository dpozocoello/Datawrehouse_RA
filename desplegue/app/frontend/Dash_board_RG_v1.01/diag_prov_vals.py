import json

with open("d:/DashboardRA/ecuador_provincias.geojson", encoding='utf-8') as f:
    geo = json.load(f)

print("=== ALL PROVINCE PROPERTY KEYS ===")
print(list(geo['features'][0]['properties'].keys()))
print("\n=== ALL PROVINCE VALUES ===")
for feat in geo['features']:
    p = feat['properties']
    # Print all key-value pairs
    print({k: v for k, v in p.items()})
