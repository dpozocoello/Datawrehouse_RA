import json

with open('f:/Datawrehouse_RA/waste_chemical_metadata.json', 'r') as f:
    d = json.load(f)

search_tables = {
    "coa_waste_generator_record": ["waste_generator_record_coa", "waste_generator_catalog"],
    "waste_dangerous": ["catalogs_waste", "generator_record", "catalogs"],
    "coa_chemical_sustances": ["chemical_sustances_records", "chemical_substances_declaration", "location_substances"],
    "chemical_pesticides": ["product_registration", "products_pqa"]
}

for schema, tables in search_tables.items():
    print(f"\n--- Schema: {schema} ---")
    for table_name in tables:
        if table_name in d.get(schema, {}):
            print(f"  Table: {table_name}")
            cols = [c['name'] for c in d[schema][table_name]['columns']]
            print(f"    Columns: {cols}")
        else:
            print(f"  Table: {table_name} NOT FOUND")
