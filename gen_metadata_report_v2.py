import json

with open('f:/Datawrehouse_RA/waste_chemical_metadata.json', 'r') as f:
    d = json.load(f)

search_tables = {
    "coa_waste_generator_record": [
        "waste_generator_record_coa", 
        "waste_generator_catalog",
        "generation_points_waste",
        "waste_waste_generation_points",
        "waste_generator_record_project_licencing_coa"
    ],
    "waste_dangerous": [
        "catalogs_waste", 
        "catalogs_waste_parent",
        "generator_record", 
        "catalogs",
        "dangerous_waste",
        "dw_classification"
    ],
    "coa_chemical_sustances": [
        "chemical_substances_declaration", 
        "chemical_sustances_records",
        "location_substances",
        "chemical_substances_movements",
        "activity_chemical_sustances"
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
            cols = d[schema][table_name]['columns']
            col_info = [f"{c['name']} ({c['type']})" for c in cols]
            report.append(f"    Columns: {col_info}")
            fks = d[schema][table_name].get('foreign_keys', [])
            if fks:
                report.append(f"    FKs: {fks}")
        else:
            report.append(f"  Table: {table_name} NOT FOUND.")

with open('f:/Datawrehouse_RA/metadata_scan_result_v2.txt', 'w') as f:
    f.write("\n".join(report))
print("Report generated in f:/Datawrehouse_RA/metadata_scan_result_v2.txt")
