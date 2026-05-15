import xml.etree.ElementTree as ET
import os

def modify_kjb():
    file_path = r"d:/Datawrehouse_RA/Jobs/JOB_CARGA_DWH_REGULARIZACION.kjb"
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return
        
    tree = ET.parse(file_path)
    root = tree.getroot()
    entries = root.find('entries')
    hops = root.find('hops')
    
    # Check if step already exists
    for entry in entries.findall('entry'):
        if entry.find('name').text == 'RGD_ETL_WRAPPER':
            print("Step RGD_ETL_WRAPPER already exists.")
            return

    # Create Shell Entry for RGD Wrapper
    entry_wrapper = ET.Element('entry')
    ET.SubElement(entry_wrapper, 'name').text = 'RGD_ETL_WRAPPER'
    ET.SubElement(entry_wrapper, 'description').text = 'Wrapper Python ETL para RGD'
    ET.SubElement(entry_wrapper, 'type').text = 'SHELL'
    ET.SubElement(entry_wrapper, 'attributes')
    ET.SubElement(entry_wrapper, 'filename')
    ET.SubElement(entry_wrapper, 'work_directory').text = r'd:\Datawrehouse_RA'
    ET.SubElement(entry_wrapper, 'arg_from_previous').text = 'N'
    ET.SubElement(entry_wrapper, 'exec_per_row').text = 'N'
    ET.SubElement(entry_wrapper, 'set_logfile').text = 'N'
    ET.SubElement(entry_wrapper, 'logfile')
    ET.SubElement(entry_wrapper, 'set_append_logfile').text = 'N'
    ET.SubElement(entry_wrapper, 'logext')
    ET.SubElement(entry_wrapper, 'add_date').text = 'N'
    ET.SubElement(entry_wrapper, 'add_time').text = 'N'
    ET.SubElement(entry_wrapper, 'insertScript').text = 'Y'
    # Executing the new python wrapper
    ET.SubElement(entry_wrapper, 'script').text = 'python rgd_etl_wrapper.py'
    ET.SubElement(entry_wrapper, 'loglevel').text = 'Basic'
    
    # UI coords
    ET.SubElement(entry_wrapper, 'parallel').text = 'N'
    ET.SubElement(entry_wrapper, 'draw').text = 'Y'
    ET.SubElement(entry_wrapper, 'nr').text = '0'
    ET.SubElement(entry_wrapper, 'xloc').text = '700'
    ET.SubElement(entry_wrapper, 'yloc').text = '500'
    
    entries.append(entry_wrapper)
    
    # Find existing hop ending in 'Exito' to insert this step before it
    hop_to_exito = None
    for hop in hops.findall('hop'):
        if hop.find('to').text == 'Exito':
            hop_to_exito = hop
            break
            
    if hop_to_exito is not None:
        # Modify existing hop to point to RGD_ETL_WRAPPER
        hop_to_exito.find('to').text = 'RGD_ETL_WRAPPER'
        
        # New hop: RGD_ETL_WRAPPER -> Exito
        hop_wrapper_exito = ET.Element('hop')
        ET.SubElement(hop_wrapper_exito, 'from').text = 'RGD_ETL_WRAPPER'
        ET.SubElement(hop_wrapper_exito, 'to').text = 'Exito'
        ET.SubElement(hop_wrapper_exito, 'from_nr').text = '0'
        ET.SubElement(hop_wrapper_exito, 'to_nr').text = '0'
        ET.SubElement(hop_wrapper_exito, 'enabled').text = 'Y'
        ET.SubElement(hop_wrapper_exito, 'evaluation').text = 'Y' # Only if success
        ET.SubElement(hop_wrapper_exito, 'unconditional').text = 'N'
        hops.append(hop_wrapper_exito)
        
        tree.write(file_path, encoding='UTF-8', xml_declaration=True)
        print("JOB_CARGA_DWH_REGULARIZACION.kjb modified successfully with RGD_ETL_WRAPPER!")
    else:
        print("Couldn't find the 'Exito' hop to inject the step.")

if __name__ == "__main__":
    modify_kjb()
