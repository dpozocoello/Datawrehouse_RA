import xml.etree.ElementTree as ET

def modify_kjb():
    file_path = r"f:/Datawrehouse_RA/Jobs/JOB_CARGA_DWH_REGULARIZACION.kjb"
    
    # Parse the XML
    tree = ET.parse(file_path)
    root = tree.getroot()
    
    entries = root.find('entries')
    hops = root.find('hops')
    
    # Create Shell Entry for Ingesta
    entry_ingesta = ET.Element('entry')
    ET.SubElement(entry_ingesta, 'name').text = 'INGESTA_WASTE_CHEMICAL'
    ET.SubElement(entry_ingesta, 'description').text = 'Ingesta v1.5 python pandas/sqlalchemy'
    ET.SubElement(entry_ingesta, 'type').text = 'SHELL'
    ET.SubElement(entry_ingesta, 'attributes')
    ET.SubElement(entry_ingesta, 'filename')
    ET.SubElement(entry_ingesta, 'work_directory').text = r'${Internal.Entry.Current.Directory}/../ETL_p'
    ET.SubElement(entry_ingesta, 'arg_from_previous').text = 'N'
    ET.SubElement(entry_ingesta, 'exec_per_row').text = 'N'
    ET.SubElement(entry_ingesta, 'set_logfile').text = 'N'
    ET.SubElement(entry_ingesta, 'logfile')
    ET.SubElement(entry_ingesta, 'set_append_logfile').text = 'N'
    ET.SubElement(entry_ingesta, 'logext')
    ET.SubElement(entry_ingesta, 'add_date').text = 'N'
    ET.SubElement(entry_ingesta, 'add_time').text = 'N'
    ET.SubElement(entry_ingesta, 'insertScript').text = 'Y'
    ET.SubElement(entry_ingesta, 'script').text = 'python ingesta/ingesta_waste_chemical.py'
    ET.SubElement(entry_ingesta, 'loglevel').text = 'Basic'
    
    # UI coords for Ingesta
    ET.SubElement(entry_ingesta, 'parallel').text = 'N'
    ET.SubElement(entry_ingesta, 'draw').text = 'Y'
    ET.SubElement(entry_ingesta, 'nr').text = '0'
    ET.SubElement(entry_ingesta, 'xloc').text = '800'
    ET.SubElement(entry_ingesta, 'yloc').text = '600'
    
    entries.append(entry_ingesta)
    
    # Create SQL Entry for Carga
    entry_carga = ET.Element('entry')
    ET.SubElement(entry_carga, 'name').text = 'SP Cargar Desechos/Quimicos'
    ET.SubElement(entry_carga, 'description').text = ''
    ET.SubElement(entry_carga, 'type').text = 'SQL'
    ET.SubElement(entry_carga, 'attributes')
    ET.SubElement(entry_carga, 'sql').text = ''
    ET.SubElement(entry_carga, 'useVariableSubstitution').text = 'F'
    ET.SubElement(entry_carga, 'sqlfromfile').text = 'T'
    ET.SubElement(entry_carga, 'sqlfilename').text = r'${Internal.Entry.Current.Directory}/../etl_waste_chemical_load.sql'
    ET.SubElement(entry_carga, 'sendOneStatement').text = 'F'
    ET.SubElement(entry_carga, 'connection').text = 'CONN_DWH_LOCAL'
    
    # UI coords for Carga
    ET.SubElement(entry_carga, 'parallel').text = 'N'
    ET.SubElement(entry_carga, 'draw').text = 'Y'
    ET.SubElement(entry_carga, 'nr').text = '0'
    ET.SubElement(entry_carga, 'xloc').text = '600'
    ET.SubElement(entry_carga, 'yloc').text = '600'
    
    entries.append(entry_carga)
    
    # Find existing hop ending in 'Exito'
    hop_to_exito = None
    for hop in hops.findall('hop'):
        if hop.find('to').text == 'Exito':
            hop_to_exito = hop
            break
            
    if hop_to_exito is not None:
        last_step_name = hop_to_exito.find('from').text
        
        # Modify existing hop to point to INGESTA
        hop_to_exito.find('to').text = 'INGESTA_WASTE_CHEMICAL'
        
        # New hop: INGESTA -> SP Carga
        hop_ingesta_carga = ET.Element('hop')
        ET.SubElement(hop_ingesta_carga, 'from').text = 'INGESTA_WASTE_CHEMICAL'
        ET.SubElement(hop_ingesta_carga, 'to').text = 'SP Cargar Desechos/Quimicos'
        ET.SubElement(hop_ingesta_carga, 'from_nr').text = '0'
        ET.SubElement(hop_ingesta_carga, 'to_nr').text = '0'
        ET.SubElement(hop_ingesta_carga, 'enabled').text = 'Y'
        ET.SubElement(hop_ingesta_carga, 'evaluation').text = 'Y'
        ET.SubElement(hop_ingesta_carga, 'unconditional').text = 'N'
        hops.append(hop_ingesta_carga)
        
        # New hop: SP Carga -> Exito
        hop_carga_exito = ET.Element('hop')
        ET.SubElement(hop_carga_exito, 'from').text = 'SP Cargar Desechos/Quimicos'
        ET.SubElement(hop_carga_exito, 'to').text = 'Exito'
        ET.SubElement(hop_carga_exito, 'from_nr').text = '0'
        ET.SubElement(hop_carga_exito, 'to_nr').text = '0'
        ET.SubElement(hop_carga_exito, 'enabled').text = 'Y'
        ET.SubElement(hop_carga_exito, 'evaluation').text = 'Y'
        ET.SubElement(hop_carga_exito, 'unconditional').text = 'N'
        hops.append(hop_carga_exito)
        
        # Write back tree preserving format
        tree.write(file_path, encoding='UTF-8', xml_declaration=True)
        print("KJB modified successfully!")
    else:
        print("Couldn't find the Exito hop.")

if __name__ == "__main__":
    modify_kjb()
