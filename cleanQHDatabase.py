#!/usr/bin/env python3
import json
import re
from pathlib import Path

class CompactListEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, list):
            # Handle numerical lists (e.g., [2683, 3326, 0])
            if all(isinstance(item, (int, float)) for item in obj):
                return '[' + ','.join(str(item) for item in obj) + ']'
            # Handle nested lists of numbers (e.g., [[2683, 3326, 0], [2684, 3323, 0]])
            if all(isinstance(item, list) and all(isinstance(subitem, (int, float)) for subitem in item) for item in obj):
                return '[' + ','.join(self.default(item) for item in obj) + ']'
            # Fallback to default JSON encoding for other lists
            return obj
        return super().default(obj)

def post_process_json(file_path):
    """Post-process JSON file to ensure worldpoints arrays are single-line with integer values."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
        # Replace multi-line worldpoints arrays with single-line versions
        pattern = r'(\[\s*\[\s*(\d+),\s*(\d+),\s*(\d+)\s*\](,\s*\[\s*(\d+),\s*(\d+),\s*(\d+)\s*\])*\s*\])'
        def replacement(match):
            # Extract all sublists of numbers
            sublists = re.findall(r'\[\s*(\d+),\s*(\d+),\s*(\d+)\s*\]', match.group(0))
            # Convert to single-line format with integers
            return '[' + ','.join(f'[{int(x)},{int(y)},{int(z)}]' for x, y, z in sublists) + ']'
        text = re.sub(pattern, replacement, text)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(text)
        print(f"Post-processed {file_path} to ensure single-line worldpoints")
    except Exception as e:
        print(f"Error post-processing {file_path}: {e}")

def deduplicate_worldpoints(worldpoints, threshold=5):
    """Deduplicate worldpoints within a threshold (Manhattan distance), keeping one point per cluster."""
    if not worldpoints:
        return worldpoints
    
    # Initialize clusters with the first point
    clusters = [[worldpoints[0]]]
    for point in worldpoints[1:]:
        x1, y1, z1 = point
        added = False
        # Check if point is close to any existing cluster
        for cluster in clusters:
            for cx, cy, cz in cluster:
                distance = abs(x1 - cx) + abs(y1 - cy)
                if distance <= threshold:
                    cluster.append(point)
                    added = True
                    break
            if added:
                break
        if not added:
            clusters.append([point])
    
    # Keep the first point from each cluster
    deduplicated = [cluster[0] for cluster in clusters]
    return deduplicated

def clean_database(input_path, cleaned_output_path, ids_output_path):
    try:
        # Read the input JSON
        with open(input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Validate input
        if not data:
            print(f"Error: Input file {input_path} is empty or invalid")
            return
        
        # Sort zones by name if present
        if 'zones' in data:
            data['zones'] = sorted(data['zones'], key=lambda z: z['name'])
        
        # Sort keys for cleaned JSON
        sorted_data = {key: data[key] for key in sorted(data.keys())}
        for key in sorted_data:
            if isinstance(sorted_data[key], dict):
                sorted_data[key] = {k: sorted_data[key][k] for k in sorted(sorted_data[key].keys())}
        
        # Write cleaned JSON with sorted keys and compact worldpoints
        try:
            with open(cleaned_output_path, 'w', encoding='utf-8') as f:
                json.dump(sorted_data, f, indent=2, cls=CompactListEncoder)
            post_process_json(cleaned_output_path)
            print(f"Generated cleaned database at {cleaned_output_path}")
        except Exception as e:
            print(f"Error generating {cleaned_output_path}: {e}")
        
        # Create lean database with only npcs, objects, and zones (without mentions)
        lean_data = {
            'npcs': {},
            'objects': {},
            'zones': {}
        }
        try:
            for key in sorted(data['npcs'].keys()):
                # Deduplicate worldpoints for NPCs only
                deduplicated_worldpoints = deduplicate_worldpoints(data['npcs'][key]['worldpoints'], threshold=5)
                lean_data['npcs'][key] = {
                    'id': data['npcs'][key]['id'],
                    'name': data['npcs'][key]['name'],
                    'worldpoints': deduplicated_worldpoints
                }
            for key in sorted(data['objects'].keys()):
                # Keep all worldpoints for objects
                lean_data['objects'][key] = {
                    'id': data['objects'][key]['id'],
                    'name': data['objects'][key]['name'],
                    'worldpoints': data['objects'][key]['worldpoints']
                }
            if 'zones' in data:
                for zone in data['zones']:
                    lean_data['zones'][zone['name']] = {
                        'worldpoints': [
                            [zone['worldpoints'][0]['x'], zone['worldpoints'][0]['y'], zone['worldpoints'][0]['plane']],
                            [zone['worldpoints'][1]['x'], zone['worldpoints'][1]['y'], zone['worldpoints'][1]['plane']]
                        ]
                    }
            
            with open(ids_output_path, 'w', encoding='utf-8') as f:
                json.dump(lean_data, f, indent=2, cls=CompactListEncoder)
            post_process_json(ids_output_path)
            print(f"Generated NPC, object, and zone database at {ids_output_path}")
        except Exception as e:
            print(f"Error generating {ids_output_path}: {e}")
    
    except Exception as e:
        print(f"Error processing {input_path}: {e}")

def main():
    script_dir = Path(__file__).parent
    default_input = script_dir / "QH_database.json"
    default_cleaned_output = script_dir / "QH_Cleaned.json"
    default_ids_output = script_dir / "worldpoints.json"
    
    # Corrected function call
    clean_database(default_input, default_cleaned_output, default_ids_output)

if __name__ == '__main__':
    main()