import json

with open('f:/Datawrehouse_RA/waste_chemical_metadata.json', 'r') as f:
    d = json.load(f)

search_tables = {
    "coa_waste_generator_record": [
        "waste_generator_record_coa", 
        "waste_generator_catalog",
        "generation_points_waste",
        "waste_waste_generation_points"
    ],
    "waste_dangerous": [
        "catalogs_waste", 
        "generator_record", 
        "catalogs",
        "dangerous_waste", # I know it wasn't listed, but in case I missed it
        "dw_classification" # Same
    ],
    "coa_chemical_sustances": [
        "chemical_sustances_records", 
        "chemical_substances_declaration", 
        "location_substances",
        "chemical_substances_movements"
    ],
    "chemical_pesticides": [
        "product_registration", 
        "products_pqa"
    ]
}

report = []
for schema, tables in search_tables.items():
    report.append(f"\n--- Schema: {schema} ---")
    for table_name in tables:
        if table_name in d.get(schema, {}):
            report.append(f"  Table: {table_name}")
            cols = [c['name'] for c in d[schema][table_name]['columns']]
            report.append(f"    Columns: {cols}")
        else:
            # Check for similar names
            matches = [t for t in d.get(schema, {}).keys() if table_name in t]
            if matches:
                report.append(f"  Table: {table_name} NOT FOUND. Matches: {matches}")
            else:
                report.append(f"  Table: {table_name} NOT FOUND.")

with open('f:/Datawrehouse_RA/metadata_scan_result.txt', 'w') as f:
    f.write("\n".join(report))
print("Report generated in f:/Datawrehouse_RA/metadata_scan_result.txt")
