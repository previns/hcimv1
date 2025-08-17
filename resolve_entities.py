#!/usr/bin/env python3
"""
resolve_entities.py
Resolves NPCs, objects, and items in quest steps using worldpoints.json.
If an NPC or object is not found, fetches the ID from local Runelite API files (NpcID.java or ObjectID.java).
Sets worldpoints to null for fetched entities and logs a comment for manual addition.
Handles item quantities, prioritizes unpoisoned item variants, and skips invalid items.
"""
import re
import json
import argparse
import sys
import difflib
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path

def const_case(name: str) -> str:
    return re.sub(r"[^A-Z0-9_]", "", name.upper().replace(" ", "_").replace("-", "_").replace("'", ""))

def fetch_runelite_id(name: str, category: str, script_dir: Path) -> Optional[Dict[str, Any]]:
    """
    Fetch NPC or object ID from local Runelite API files (NpcID.java or ObjectID.java).
    Returns a dict with name, id, and null worldpoints if found, else None.
    """
    default_npc_ids = script_dir / "runelite" / "runelite-api" / "src" / "main" / "java" / "net" / "runelite" / "api" / "gameval" / "NpcID.java"
    default_object_ids = script_dir / "runelite" / "runelite-api" / "src" / "main" / "java" / "net" / "runelite" / "api" / "gameval" / "ObjectID.java"

    if category == "npcs":
        file_path = default_npc_ids
    elif category == "objects":
        file_path = default_object_ids
    else:
        return None

    if not file_path.exists():
        print(f"Warning: {file_path} not found for {category} ID fetching", file=sys.stderr)
        return None

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = f.read()
        # Parse for ID, looking for comment with name or constant definition
        pattern = r'/\*\*\n\s*\*\s*(.+?)\n\s*\*/\n\s*public static final int (\w+) = (\d+);'
        name_lower = name.lower().replace("'", "")  # Remove apostrophes for matching
        for match in re.finditer(pattern, data, re.MULTILINE):
            comment_name = match.group(1).strip().lower().replace("'", "")
            constant = match.group(2)
            id_str = match.group(3)
            if name_lower in comment_name or name_lower.replace(" ", "_") in constant.lower():
                return {
                    "name": name,
                    "id": int(id_str),
                    "worldpoints": None,  # Use null for Java output
                    "comment": f"World points for {name} (ID {id_str}) need to be manually added in QuestFromWiki.java"
                }
        return None
    except Exception as e:
        print(f"Warning: Failed to fetch {category} ID for '{name}' from {file_path}: {e}", file=sys.stderr)
        return None

def load_entities(world_path: str, category: str) -> Dict[str, List[Dict[str, Any]]]:
    entities = {}
    def add_entry(name, entry):
        if not name:
            return
        key = name.strip().lower()
        rec = {
            "name": entry.get("name", name),
            "id": entry.get("id"),
            "worldpoints": entry.get("worldpoints") or entry.get("points") or entry.get("locations") or None,
            "comment": entry.get("comment")
        }
        entities.setdefault(key, []).append(rec)

    # Load worldpoints.json
    if Path(world_path).exists():
        with open(world_path, "r", encoding="utf-8", errors="ignore") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError as e:
                print(f"Error: Failed to parse {world_path}: {e}", file=sys.stderr)
                raise
        if isinstance(data, dict):
            if category in data and isinstance(data[category], dict):
                for k, v in data[category].items():
                    add_entry(v.get("name") or k, v)
            else:
                for k, v in data.items():
                    if isinstance(v, dict) and ("id" in v or "worldpoints" in v or "points" in v):
                        add_entry(v.get("name") or k, v)
        elif isinstance(data, list):
            for v in data:
                if isinstance(v, dict) and "name" in v:
                    add_entry(v["name"], v)
    else:
        print(f"Warning: {world_path} not found", file=sys.stderr)

    return entities

def load_items(path: str) -> Dict[str, Tuple[str, str]]:
    items = {}
    if Path(path).exists():
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError as e:
                print(f"Error: Failed to parse {path}: {e}", file=sys.stderr)
                raise
        if isinstance(data, dict):
            inner = data.get("items", data)
            if isinstance(inner, dict):
                for k, v in inner.items():
                    if isinstance(v, str) and v.isdigit():
                        items[k.strip().lower()] = (k.strip(), v)
    else:
        print(f"Error: {path} not found", file=sys.stderr)
        raise FileNotFoundError(f"{path} not found")
    return items

def resolve_entity(name: str, entdict: Dict[str, List[Dict[str, Any]]], category: str, cutoff=0.9) -> List[Dict[str, Any]]:
    script_dir = Path(__file__).parent
    key = name.strip().lower()
    if key in entdict:
        return entdict[key]
    candidates = difflib.get_close_matches(key, entdict.keys(), n=3, cutoff=cutoff)
    res = []
    for c in candidates:
        res.extend(entdict[c])
    if not res:
        # Fetch ID from local Runelite API files
        entity_data = fetch_runelite_id(name, category, script_dir)
        if entity_data:
            print(f"Added {category} '{name}' with ID {entity_data['id']} from Runelite API (null world point). Add world points manually in QuestFromWiki.java.", file=sys.stderr)
            return [entity_data]
        print(f"Warning: No match for entity '{name}' in {category}", file=sys.stderr)
    return res

def expand_slash_variants(name: str) -> List[str]:
    if "/" in name:
        parts = [p.strip() for p in name.split("/") if p.strip()]
        return parts
    return [name]

def normalize_item_name(name: str) -> List[str]:
    k = name.strip().lower()
    k = re.sub(r"^(the|a|an)\s+", "", k, re.I)
    k = re.sub(r"\s*\(\d+\s+inventory\s+slots?\)", "", k, re.I)
    k = re.sub(r"\(.*?\)", "", k).strip()
    if k.lower() in ["spade chisel", "jug bowl"]:
        return [part.strip().title() for part in k.split(" ") if part.strip()]
    if k.lower() in ["air rune", "mind rune"]:
        k = k + "s"  # Convert to plural: "Air Runes", "Mind Runes"
    if k.lower() == "empty jug":
        k = "jug"
    if k.lower() == "sword":
        k = "iron sword"
    if k.lower() == "ghost speak amulet":
        k = "ghostspeak amulet"
    return [k.title()]

def resolve_item(item: Dict[str, Any], itemdict: Dict[str, Tuple[str, str]], cutoff=0.9) -> List[Tuple[str, str, str, int]]:
    name = item["name"]
    if not name or name.strip() == "":
        return []
    quantity = item.get("quantity", 1)
    normalized_names = normalize_item_name(name)
    results = []
    for norm_name in normalized_names:
        norm_lower = norm_name.lower()
        # Skip non-item terms
        non_item_terms = {
            "talk", "to", "head", "north", "west", "east", "south", "pickpocket", "drop",
            "and", "claim", "more", "sell", "buy", "start", "on", "complete", "first",
            "step", "install", "quest", "helper", "plug", "in", "runelite", "check",
            "playtime", "go", "upstairs", "again", "collect", "bank", "at", "castle",
            "top", "floor", "deposit", "all", "keep", "your", "for", "later", "move",
            "into", "slot", "slots", "click", "lock", "always", "set", "placeholders",
            "pin", "count", "randoms", "or", "delete", "from", "tutorial", "island",
            "withdraw", "down", "staircase", "twice", "fill", "sink", "kitchen",
            "kill", "giant", "rat", "with", "wind", "strike", "towards", "draynor",
            "hugging", "fence", "avoid", "jail", "guards", "swamp", "wield", "this",
            "table", "inside", "his", "house", "wizards", "tower", "off", "next",
            "stairs", "basement", "continue", "everything", "make", "sure", "you",
            "get", "else", "hop", "worlds", "repeat", "return", "obtain", "right",
            "click", "shop", "settings", "disable", "level", "up", "general", "store",
            "marks", "spot", "veos", "chicken", "lumbridge", "rune mysteries",
            "monk's friend", "family crest quest", "client of kourend + druidic ritual",
            "tree gnome village", "x marks the spot", "restless ghost", "druidic ritual",
            "lumbridge easy diary", "man", "woman", "empty", "take", "forestry", "kit",
            "1", "2", "3", "(", ")", "sword", "ghost", "speak", "gloves", "boots", "2nd", "of", "-", "x"
        }
        if norm_lower in non_item_terms:
            continue
        # Check for explicit poisoned variant
        is_poisoned = "(p)" in name.lower() or "poison" in name.lower()
        # Prefer unpoisoned variant unless explicitly poisoned
        unp_key = f"{norm_lower}#(unp)"
        if not is_poisoned and unp_key in itemdict:
            canonical, item_id = itemdict[unp_key]
            if item_id.isdigit():
                results.append((name, canonical, item_id, quantity))
            continue
        # Direct match
        if norm_lower in itemdict:
            canonical, item_id = itemdict[norm_lower]
            if item_id.isdigit():
                results.append((name, canonical, item_id, quantity))
            continue
        # Special handling for "Treasure Scroll"
        if "treasure scroll" in norm_lower:
            candidates = difflib.get_close_matches("clue scroll (beginner)", itemdict.keys(), n=1, cutoff=cutoff)
            if candidates:
                canonical, item_id = itemdict[candidates[0]]
                if item_id.isdigit():
                    results.append((name, canonical, item_id, quantity))
        else:
            # Fuzzy match, preferring unpoisoned if available
            candidates = difflib.get_close_matches(norm_lower, itemdict.keys(), n=1, cutoff=cutoff)
            for cand in candidates:
                if not is_poisoned and "#(unp)" in cand:
                    canonical, item_id = itemdict[cand]
                    if item_id.isdigit():
                        results.append((name, canonical, item_id, quantity))
                        break
            else:
                if candidates:
                    canonical, item_id = itemdict[candidates[0]]
                    if item_id.isdigit():
                        results.append((name, canonical, item_id, quantity))
        if not results:
            print(f"Warning: No match for item '{name}' in item database", file=sys.stderr)
    return results

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--steps", required=True)
    ap.add_argument("--world", required=True)
    ap.add_argument("--items", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    try:
        steps = json.load(open(args.steps, "r", encoding="utf-8"))
    except FileNotFoundError:
        print(f"Error: {args.steps} not found", file=sys.stderr)
        raise
    except json.JSONDecodeError as e:
        print(f"Error: Failed to parse {args.steps}: {e}", file=sys.stderr)
        raise

    npcdict = load_entities(args.world, "npcs")
    objectdict = load_entities(args.world, "objects")
    itemdict = load_items(args.items)

    for s in steps:
        s["npc_matches"] = []
        s["object_matches"] = []
        s["item_matches"] = []
        for name in s.get("npc_names", []):
            for n in expand_slash_variants(name):
                matches = resolve_entity(n, npcdict, "npcs")
                if matches:
                    for m in matches:
                        s["npc_matches"].append({
                            "query": n,
                            "name": m.get("name"),
                            "id": m.get("id"),
                            "worldpoints": m.get("worldpoints"),
                            "comment": m.get("comment")
                        })
        for name in s.get("object_names", []):
            for n in expand_slash_variants(name):
                matches = resolve_entity(n, objectdict, "objects")
                if matches:
                    for m in matches:
                        s["object_matches"].append({
                            "query": n,
                            "name": m.get("name"),
                            "id": m.get("id"),
                            "worldpoints": m.get("worldpoints"),
                            "comment": m.get("comment")
                        })
        for item in s.get("items", []):
            matches = resolve_item(item, itemdict)
            for query, canonical, item_id, quantity in matches:
                s["item_matches"].append({
                    "query": query,
                    "canonical_name": canonical,
                    "item_id": item_id,
                    "quantity": quantity
                })
        if s["npc_matches"]:
            m = s["npc_matches"][0]
            s["npc_name_resolved"] = m["name"]
            s["npc_id"] = m["id"]
            s["npc_id_const"] = const_case(m["name"])
            s["worldpoint"] = m["worldpoints"]
            if m.get("comment"):
                s["comment"] = m["comment"]
        if s["object_matches"]:
            m = s["object_matches"][0]
            s["object_name_resolved"] = m["name"]
            s["object_id"] = m["id"]
            s["object_id_const"] = const_case(m["name"])
            s["worldpoint"] = m["worldpoints"]
            if m.get("comment"):
                s["comment"] = m["comment"]
        if s["item_matches"]:
            s["items_required"] = [m["query"] for m in s["item_matches"]]

    with open(args.out, "w", encoding="utf-8") as w:
        json.dump(steps, w, ensure_ascii=False, indent=2)
    print(f"Enriched {len(steps)} steps -> {args.out}")

if __name__ == "__main__":
    main()