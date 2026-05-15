import json

with open('f:/Datawrehouse_RA/waste_chemical_metadata.json', 'r') as f:
    d = json.load(f)

for schema, tables in d.items():
    print(f"\n--- Schema: {schema} ---")
    for table in sorted(tables.keys()):
        print(f"  - {table}")
