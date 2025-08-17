#!/usr/bin/env python3
import argparse
import json
import re
from pathlib import Path
from multiprocessing import Pool, cpu_count
from tqdm import tqdm

# Combined regex pattern for efficiency
INT_RE = r"-?\d+"
COMBINED_RE = re.compile(
    r'(?:new\s+WorldPoint\s*\(\s*(' + INT_RE + r')\s*,\s*(' + INT_RE + r')\s*(?:,\s*(' + INT_RE + r')\s*)?\))|' +
    r'(WorldPoint\.(?:fromRegion|fromLocal|fromChunk|from(?:\w+))\s*\(([^)]*)\))|' +
    r'(new\s+ObjectStep\(.*?(?:ObjectID|QHObjectID)\.([A-Za-z0-9_]+),\s*new\s+WorldPoint\s*\(\s*(' + INT_RE + r')\s*,\s*(' + INT_RE + r')\s*(?:,\s*(' + INT_RE + r')\s*)?\))|' +
    r'(new\s+NpcStep\(.*?NpcID\.([A-Za-z0-9_]+),\s*new\s+WorldPoint\s*\(\s*(' + INT_RE + r')\s*,\s*(' + INT_RE + r')\s*(?:,\s*(' + INT_RE + r')\s*)?\))|' +
    r'(=\s*new\s+Zone\(new\s+WorldPoint\s*\(\s*(' + INT_RE + r')\s*,\s*(' + INT_RE + r')\s*(?:,\s*(' + INT_RE + r')\s*)?\),\s*new\s+WorldPoint\s*\(\s*(' + INT_RE + r')\s*,\s*(' + INT_RE + r')\s*(?:,\s*(' + INT_RE + r')\s*)?\))|' +
    r'\b(NpcID|ObjectID|QHObjectID)\.([A-Za-z0-9_]+)\b'
)

# Regex for capturing comments above ID declarations or uncommented declarations
COMMENT_RE = re.compile(
    r'(?://\s*(.*?)\s*\n\s*public\s+static\s+final\s+int\s+(\w+)\s*=\s*(\d+|ObjectID\.([A-Za-z0-9_]+));\s*$)|' +  # Single-line comment
    r'(/\*\*\s*\n\s*\*\s*(.*?)\s*\n\s*\*/\s*\n\s*public\s+static\s+final\s+int\s+(\w+)\s*=\s*(\d+|ObjectID\.([A-Za-z0-9_]+));\s*$)|' +  # Multi-line comment
    r'(?:^\s*public\s+static\s+final\s+int\s+(\w+)\s*=\s*(\d+|ObjectID\.([A-Za-z0-9_]+));\s*$)',  # No comment
    re.MULTILINE
)

def parse_ints(argtext):
    return [int(x) for x in re.findall(INT_RE, argtext)]

def load_id_files(npc_path, object_path, custom_object_path, qh_object_path):
    maps = {'npcs': {}, 'objects': {}}
    
    # Parse NpcID.java
    if npc_path.exists():
        with open(npc_path, 'r', encoding='utf-8') as f:
            text = f.read()
        for match in COMMENT_RE.finditer(text):
            if match.group(1):  # Single-line comment
                comment, name, id_val = match.group(1), match.group(2), match.group(3)
            elif match.group(5):  # Multi-line comment
                comment, name, id_val = match.group(6), match.group(7), match.group(8)
            else:  # No comment
                comment, name, id_val = None, match.group(10), match.group(11)
            if id_val.startswith('ObjectID.'):
                obj_key = id_val.split('.')[1]
                print(f"Warning: Unexpected ObjectID.{obj_key} reference in {npc_path}")
                continue
            maps['npcs'][name] = {
                'id': int(id_val),
                'name': comment.strip() if comment and comment.strip() else name.replace('_', ' ')
            }
    
    # Parse ObjectID.java
    if object_path.exists():
        with open(object_path, 'r', encoding='utf-8') as f:
            text = f.read()
        for match in COMMENT_RE.finditer(text):
            if match.group(1):  # Single-line comment
                comment, name, id_val = match.group(1), match.group(2), match.group(3)
            elif match.group(5):  # Multi-line comment
                comment, name, id_val = match.group(6), match.group(7), match.group(8)
            else:  # No comment
                comment, name, id_val = None, match.group(10), match.group(11)
            if id_val.startswith('ObjectID.'):
                obj_key = id_val.split('.')[1]
                print(f"Warning: Unexpected ObjectID.{obj_key} reference in {object_path}")
                continue
            maps['objects'][name] = {
                'id': int(id_val),
                'name': comment.strip() if comment and comment.strip() else name.replace('_', ' ')
            }
    
    # Parse ObjectID1.java
    if custom_object_path.exists():
        with open(custom_object_path, 'r', encoding='utf-8') as f:
            text = f.read()
        custom_ids = []
        for match in COMMENT_RE.finditer(text):
            if match.group(1):  # Single-line comment
                comment, name, id_val = match.group(1), match.group(2), match.group(3)
            elif match.group(5):  # Multi-line comment
                comment, name, id_val = match.group(6), match.group(7), match.group(8)
            else:  # No comment
                comment, name, id_val = None, match.group(10), match.group(11)
            if id_val.startswith('ObjectID.'):
                obj_key = id_val.split('.')[1]
                print(f"Warning: Unexpected ObjectID.{obj_key} reference in {custom_object_path}")
                continue
            if name not in maps['objects']:
                maps['objects'][name] = {
                    'id': int(id_val),
                    'name': comment.strip() if comment and comment.strip() else name.replace('_', ' ')
                }
                custom_ids.append(name)
        print(f"Loaded {len(custom_ids)} custom ObjectIDs from {custom_object_path}: {custom_ids}")
    else:
        print(f"Warning: {custom_object_path} not found, skipping custom ObjectIDs")
    
    # Parse QHObjectID.java
    if qh_object_path.exists():
        with open(qh_object_path, 'r', encoding='utf-8') as f:
            text = f.read()
        qh_ids = []
        for match in COMMENT_RE.finditer(text):
            if match.group(1):  # Single-line comment
                comment, name, id_val, obj_ref = match.group(1), match.group(2), match.group(3), match.group(4)
            elif match.group(5):  # Multi-line comment
                comment, name, id_val, obj_ref = match.group(6), match.group(7), match.group(8), match.group(9)
            else:  # No comment
                comment, name, id_val, obj_ref = None, match.group(10), match.group(11), match.group(12)
            if id_val.startswith('ObjectID.'):
                obj_key = id_val.split('.')[1]
                if obj_key in maps['objects']:
                    id_val = maps['objects'][obj_key]['id']
                else:
                    print(f"Warning: ObjectID.{obj_key} referenced in {qh_object_path} but not found in ObjectID.java")
                    continue
            if name not in maps['objects']:
                maps['objects'][name] = {
                    'id': int(id_val),
                    'name': comment.strip() if comment and comment.strip() else name.replace('_', ' ')
                }
                qh_ids.append(name)
        print(f"Loaded {len(qh_ids)} custom ObjectIDs from {qh_object_path}: {qh_ids}")
    else:
        print(f"Warning: {qh_object_path} not found, skipping QH ObjectIDs")
    
    return maps

def truncate_path(fullpath, base_marker="quest-helper-master"):
    return fullpath.name

def process_file(args):
    jf, idmaps = args
    results = {
        'wps': [],
        'zones': [],
        'npcs': {},
        'objects': {},
        'missing_ids': [],
        'invalid_zones': []  # Track invalid zones
    }
    
    try:
        text = jf.read_text(encoding='utf-8', errors='ignore')
        lines = text.splitlines()
        file_path = truncate_path(jf)
        quest_name = jf.stem
        
        for match in COMBINED_RE.finditer(text):
            line_no = text[:match.start()].count('\n') + 1
            line_text = lines[line_no - 1] if 0 <= line_no - 1 < len(lines) else ""
            line_text = line_text.replace('\t', '    ').strip()
            
            # WorldPoint (direct)
            if match.group(1) is not None:
                results['wps'].append({
                    'x': int(match.group(1)),
                    'y': int(match.group(2)),
                    'plane': int(match.group(3) or 0),
                    'file': file_path,
                    'line': line_no,
                    'line_text': line_text
                })
            
            # WorldPoint (fromRegion, fromLocal, etc.)
            elif match.group(4) is not None:
                ints = parse_ints(match.group(5))
                if len(ints) >= 4:
                    rx, ry, lx, ly = ints[:4]
                    plane = ints[4] if len(ints) >= 5 else 0
                    results['wps'].append({
                        'x': rx * 64 + lx,
                        'y': ry * 64 + ly,
                        'plane': plane,
                        'file': file_path,
                        'line': line_no,
                        'line_text': line_text
                    })
                elif len(ints) >= 2:
                    results['wps'].append({
                        'x': ints[0],
                        'y': ints[1],
                        'plane': ints[2] if len(ints) >= 3 else 0,
                        'file': file_path,
                        'line': line_no,
                        'line_text': line_text
                    })
            
            # ObjectStep
            elif match.group(6) is not None:
                obj_key = match.group(7)
                if obj_key not in idmaps['objects']:
                    results['missing_ids'].append(('ObjectID', obj_key, file_path))
                    print(f"Warning: ObjectID {obj_key} not found in idmaps for {file_path}")
                    continue
                obj_info = idmaps['objects'].get(obj_key, {})
                obj_name = obj_info.get('name', obj_key.replace('_', ' '))
                obj_id = obj_info.get('id')
                wp = [int(match.group(8)), int(match.group(9)), int(match.group(10) or 0)]
                results['wps'].append({
                    'x': wp[0],
                    'y': wp[1],
                    'plane': wp[2],
                    'file': file_path,
                    'line': line_no,
                    'line_text': line_text,
                    'entity': {'kind': 'objects', 'name': obj_name, 'id': obj_id}
                })
                if obj_key not in results['objects']:
                    results['objects'][obj_key] = {
                        'id': obj_id,
                        'name': obj_name,
                        'worldpoints': [],
                        'mentions': []
                    }
                results['objects'][obj_key]['worldpoints'].append(wp)
                results['objects'][obj_key]['mentions'].append({
                    'file': file_path,
                    'line': line_no,
                    'line_text': line_text
                })
            
            # NpcStep
            elif match.group(11) is not None:
                npc_key = match.group(12)
                if npc_key not in idmaps['npcs']:
                    results['missing_ids'].append(('NpcID', npc_key, file_path))
                    print(f"Warning: NpcID {npc_key} not found in idmaps for {file_path}")
                    continue
                npc_info = idmaps['npcs'].get(npc_key, {})
                npc_name = npc_info.get('name', npc_key.replace('_', ' '))
                npc_id = npc_info.get('id')
                wp = [int(match.group(13)), int(match.group(14)), int(match.group(15) or 0)]
                results['wps'].append({
                    'x': wp[0],
                    'y': wp[1],
                    'plane': wp[2],
                    'file': file_path,
                    'line': line_no,
                    'line_text': line_text,
                    'entity': {'kind': 'npcs', 'name': npc_name, 'id': npc_id}
                })
                if npc_key not in results['npcs']:
                    results['npcs'][npc_key] = {
                        'id': npc_id,
                        'name': npc_name,
                        'worldpoints': [],
                        'mentions': []
                    }
                results['npcs'][npc_key]['worldpoints'].append(wp)
                results['npcs'][npc_key]['mentions'].append({
                    'file': file_path,
                    'line': line_no,
                    'line_text': line_text
                })
            
            # Zone
            elif match.group(16) is not None:
                var_line = lines[line_no - 1]
                variable_name_match = re.search(r'(\w+)\s*=\s*new\s+Zone', var_line)
                variable_name = variable_name_match.group(1) if variable_name_match else "UnknownZone"
                enhanced_name = f"{variable_name}{quest_name}"
                wp1 = {'x': int(match.group(17)), 'y': int(match.group(18)), 'plane': int(match.group(19) or 0)}
                wp2 = {'x': int(match.group(20)), 'y': int(match.group(21)), 'plane': int(match.group(22) or 0)}
                # Validate zone coordinates
                if wp1['x'] < 0 or wp1['y'] < 0 or wp2['x'] < 0 or wp2['y'] < 0:
                    results['invalid_zones'].append({
                        'name': enhanced_name,
                        'file': file_path,
                        'line': line_no,
                        'issue': 'Negative coordinates detected'
                    })
                    print(f"Warning: Invalid zone coordinates in {file_path} at line {line_no}: {line_text}")
                    continue
                if variable_name == "UnknownZone":
                    results['invalid_zones'].append({
                        'name': enhanced_name,
                        'file': file_path,
                        'line': line_no,
                        'issue': 'Failed to parse variable name'
                    })
                    print(f"Warning: Unknown zone name in {file_path} at line {line_no}: {line_text}")
                results['zones'].append({
                    'name': enhanced_name,
                    'worldpoints': [wp1, wp2],
                    'file': file_path,
                    'line': line_no,
                    'line_text': line_text
                })
            
            # NpcID, ObjectID, or QHObjectID
            elif match.group(23) is not None:
                entity_key = match.group(24)
                kind = 'npcs' if match.group(23) == 'NpcID' else 'objects'
                if entity_key not in idmaps[kind]:
                    results['missing_ids'].append((kind[:-1].capitalize() + 'ID', entity_key, file_path))
                    print(f"Warning: {kind[:-1].capitalize()}ID {entity_key} not found in idmaps for {file_path}")
                    continue
                entity_info = idmaps[kind].get(entity_key, {})
                entity_name = entity_info.get('name', entity_key.replace('_', ' '))
                entity_id = entity_info.get('id')
                if entity_key not in results[kind]:
                    results[kind][entity_key] = {
                        'id': entity_id,
                        'name': entity_name,
                        'worldpoints': [],
                        'mentions': []
                    }
                results[kind][entity_key]['mentions'].append({
                    'file': file_path,
                    'line': line_no,
                    'line_text': line_text
                })
        
        return results
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return results

def aggregate_results(results_list):
    aggregated = {
        'npcs': {},
        'objects': {},
        'worldpoints': [],
        'zones': [],
        'missing_ids': [],
        'invalid_zones': []
    }
    
    for res in results_list:
        for key, data in res['npcs'].items():
            if key not in aggregated['npcs']:
                aggregated['npcs'][key] = {
                    'id': data['id'],
                    'name': data['name'],
                    'worldpoints': [],
                    'mentions': []
                }
            aggregated['npcs'][key]['worldpoints'].extend(data['worldpoints'])
            aggregated['npcs'][key]['mentions'].extend(data['mentions'])
        
        for key, data in res['objects'].items():
            if key not in aggregated['objects']:
                aggregated['objects'][key] = {
                    'id': data['id'],
                    'name': data['name'],
                    'worldpoints': [],
                    'mentions': []
                }
            aggregated['objects'][key]['worldpoints'].extend(data['worldpoints'])
            aggregated['objects'][key]['mentions'].extend(data['mentions'])
        
        aggregated['worldpoints'].extend(res['wps'])
        aggregated['zones'].extend(res['zones'])
        aggregated['missing_ids'].extend(res['missing_ids'])
        aggregated['invalid_zones'].extend(res['invalid_zones'])
    
    # Deduplicate worldpoints
    for key, data in aggregated['npcs'].items():
        data['worldpoints'] = [list(t) for t in {tuple(wp) for wp in data['worldpoints']}]
    
    for key, data in aggregated['objects'].items():
        data['worldpoints'] = [list(t) for t in {tuple(wp) for wp in data['worldpoints']}]
    
    return aggregated

class CompactListEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, list):
            if all(isinstance(item, (int, float)) for item in obj):
                return '[' + ','.join(str(item) for item in obj) + ']'
            if all(isinstance(item, list) for item in obj):
                return '[' + ','.join(self.default(item) for item in obj) + ']'
            return obj
        return super().default(obj)

def main():
    script_dir = Path(__file__).parent
    default_src = script_dir / "quest-helper-master" / "src" / "main" / "java" / "com" / "questhelper" / "helpers"
    default_npc_ids = script_dir / "runelite" / "runelite-api" / "src" / "main" / "java" / "net" / "runelite" / "api" / "gameval" / "NpcID.java"
    default_object_ids = script_dir / "runelite" / "runelite-api" / "src" / "main" / "java" / "net" / "runelite" / "api" / "gameval" / "ObjectID.java"
    default_custom_object_ids = script_dir / "runelite" / "runelite-api" / "src" / "main" / "java" / "net" / "runelite" / "api" / "gameval" / "ObjectID1.java"
    default_qh_object_ids = script_dir / "quest-helper-master" / "src" / "main" / "java" / "com" / "questhelper" / "util" / "QHObjectID.java"
    default_out = script_dir / 'QH_database.json'

    parser = argparse.ArgumentParser(description="Scrape Quest Helper Java files for NPCs, objects, zones, and worldpoints.")
    parser.add_argument('--src', default=default_src, type=Path)
    parser.add_argument('--npc_ids', default=default_npc_ids, type=Path)
    parser.add_argument('--object_ids', default=default_object_ids, type=Path)
    parser.add_argument('--custom_object_ids', default=default_custom_object_ids, type=Path)
    parser.add_argument('--qh_object_ids', default=default_qh_object_ids, type=Path)
    parser.add_argument('--out', default=default_out, type=Path)
    args = parser.parse_args()

    idmaps = load_id_files(args.npc_ids, args.object_ids, args.custom_object_ids, args.qh_object_ids)
    java_files = list(args.src.rglob('*.java'))
    
    print(f"Scanning {len(java_files)} Java files...")
    
    with Pool(processes=cpu_count()) as pool:
        results_list = list(tqdm(
            pool.imap_unordered(process_file, [(jf, idmaps) for jf in java_files]),
            total=len(java_files),
            desc="Processing Java Files"
        ))
    
    aggregated = aggregate_results(results_list)
    
    # Print summary of missing IDs
    if aggregated['missing_ids']:
        print("\nMissing IDs:")
        for kind, entity_key, file_path in aggregated['missing_ids']:
            print(f"{kind} {entity_key} missing in {file_path}")
        print(f"Total missing IDs: {len(aggregated['missing_ids'])}")
    else:
        print("\nAll NPCs and Object IDs found in idmaps!")
    
    # Print summary of invalid zones
    if aggregated['invalid_zones']:
        print("\nInvalid Zones:")
        for zone in aggregated['invalid_zones']:
            print(f"Zone {zone['name']} in {zone['file']} at line {zone['line']}: {zone['issue']}")
        print(f"Total invalid zones: {len(aggregated['invalid_zones'])}")
    else:
        print("\nAll zones parsed successfully!")
    
    # Save missing IDs to a log file
    if aggregated['missing_ids']:
        with open(script_dir / "missing_ids.log", "w", encoding='utf-8') as f:
            for kind, entity_key, file_path in aggregated['missing_ids']:
                f.write(f"{kind} {entity_key} missing in {file_path}\n")
    
    # Save invalid zones to a log file
    if aggregated['invalid_zones']:
        with open(script_dir / "invalid_zones.log", "w", encoding='utf-8') as f:
            for zone in aggregated['invalid_zones']:
                f.write(f"Zone {zone['name']} in {zone['file']} at line {zone['line']}: {zone['issue']}\n")
    
    with open(args.out, 'w', encoding='utf-8') as f:
        json.dump(aggregated, f, indent=2, cls=CompactListEncoder)
    
    print(f"Database generated at {args.out}")

if __name__ == '__main__':
    main()