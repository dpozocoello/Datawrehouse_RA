import json

with open('f:/Datawrehouse_RA/waste_chemical_metadata.json', 'r') as f:
    d = json.load(f)

search_schemas = ['coa_waste_generator_record', 'coa_chemical_sustances', 'waste_dangerous', 'chemical_pesticides']

def search_potential_project_codes():
    print("Searching for potential project code columns...")
    for schema in search_schemas:
        if schema not in d: continue
        print(f"\n--- Schema: {schema} ---")
        for table, meta in d[schema].items():
            for col in meta['columns']:
                cname = col['name'].lower()
                ctype = col['type'].lower()
                # Looking for columns that might contain 'MAATE-RA-...' or similar
                if ('code' in cname or 'number' in cname or 'ident' in cname or 'proc' in cname) and 'char' in ctype:
                    print(f"  {table}.{col['name']} ({col['type']})")

if __name__ == "__main__":
    search_potential_project_codes()
