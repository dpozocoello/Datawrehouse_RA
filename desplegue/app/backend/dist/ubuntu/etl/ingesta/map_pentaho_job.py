import xml.etree.ElementTree as ET
import json
import os

def parse_pentaho_job(kjb_path):
    try:
        tree = ET.parse(kjb_path)
        root = tree.getroot()
        
        # 1. Map Entries
        entries = {}
        for entry in root.findall(".//entry"):
            name = entry.find("name").text
            etype = entry.find("type").text
            entries[name] = {
                "type": etype,
                "description": entry.find("description").text if entry.find("description") is not None else ""
            }
            # Special logic for SQL
            sql_node = entry.find("sql")
            if sql_node is not None:
                entries[name]["sql"] = sql_node.text
            # Special logic for Python (Shell)
            if etype == "SHELL":
                script_node = entry.find("script")
                if script_node is not None:
                    entries[name]["script"] = script_node.text
                else:
                    arg_nodes = entry.findall("./arguments/argument")
                    entries[name]["args"] = [a.text for a in arg_nodes]

        # 2. Map Hops
        hops = []
        for hop in root.findall(".//hop"):
            if hop.find("enabled").text == "Y":
                hops.append({
                    "from": hop.find("from").text,
                    "to": hop.find("to").text,
                    "unconditional": hop.find("unconditional").text == "Y"
                })
        
        # 3. Print mapping
        print(f"Loaded {len(entries)} entries and {len(hops)} hops.")
        
        # Determine sequence
        current = "START"
        visited = set()
        print("/nSEQUENCE OF ETL:")
        while current and current not in visited:
            print(f" -> [{current}] ({entries.get(current, {}).get('type', 'Unknown')})")
            visited.add(current)
            next_hop = next((h for h in hops if h['from'] == current), None)
            current = next_hop['to'] if next_hop else None
            
        return entries, hops
    except Exception as e:
        print(f"Error parsing KJB: {e}")
        return None, None

if __name__ == "__main__":
    parse_pentaho_job(r'/opt/eco-sieaa/Jobs/JOB_CARGA_DWH_REGULARIZACION.kjb')
