import xml.etree.ElementTree as ET
import json
import re

def parse_kml(kml_path):
    # Register namespaces
    namespaces = {'kml': 'http://www.opengis.net/kml/2.2'}
    
    tree = ET.parse(kml_path)
    root = tree.getroot()
    
    features = []
    
    # Find all Placemarks
    for placemark in root.findall('.//kml:Placemark', namespaces):
        name_elem = placemark.find('kml:name', namespaces)
        name = name_elem.text if name_elem is not None else "Unknown"
        
        # Look for Polygon coordinates
        coords_elem = placemark.find('.//kml:coordinates', namespaces)
        if coords_elem is not None:
            coords_text = coords_elem.text.strip()
            # KML coordinates are Lon,Lat,Alt separated by spaces
            coord_pairs = []
            for pair in re.split(r'\s+', coords_text):
                parts = pair.split(',')
                if len(parts) >= 2:
                    try:
                        lon = float(parts[0])
                        lat = float(parts[1])
                        coord_pairs.append([lat, lon]) # Leaflet/Folium uses [Lat, Lon]
                    except ValueError:
                        continue
            
            if coord_pairs:
                features.append({
                    "name": name,
                    "type": "Polygon",
                    "coordinates": coord_pairs
                })
                
    return features

if __name__ == "__main__":
    import os
    kml_file = "database/sub_zones.kml"
    output_file = "database/sub_zones.json"
    
    if os.path.exists(kml_file):
        print(f"Parsing {kml_file}...")
        zones = parse_kml(kml_file)
        with open(output_file, 'w') as f:
            json.dump(zones, f)
        print(f"Saved {len(zones)} zones to {output_file}")
    else:
        print(f"Error: {kml_file} not found")
