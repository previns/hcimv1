#!/usr/bin/env python3
"""
resolve_entities.py
Updated version with improvements:
- Load objects similarly to npcs
- Resolve object_names to object_matches
- Pick first match for npc/object, set resolved fields: npc_id_const, worldpoint, etc.
- For items, strip quantity (e.g., '3x'), inventory slots (e.g., '(8 Inventory slots)'), and normalize plurals
- Set s["items_required"] from matched queries
- Use fuzzy cutoff 0.6 for items to match 'Air Runes' to 'Air rune'
- Split compound items like 'Spade Chisel' into separate items
- Special handling for 'Treasure Scroll' to map to specific step IDs
"""
import re
import json
import argparse
import sys
import difflib
from typing import Dict, Any, List, Optional, Tuple

def const_case(name: str) -> str:
    return re.sub(r"[^A-Z0-9_]", "", name.upper().replace(" ", "_").replace("-", "_").replace("'", ""))

def load_entities(path: str, category: str) -> Dict[str, List[Dict[str, Any]]]:
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        data = json.load(f)
    entities = {}
    def add_entry(name, entry):
        if not name:
            return
        key = name.strip().lower()
        rec = {
            "name": entry.get("name", name),
            "id": entry.get("id"),
            "worldpoints": entry.get("worldpoints") or entry.get("points") or entry.get("locations") or []
        }
        entities.setdefault(key, []).append(rec)
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
    return entities

def load_items(path: str) -> Dict[str, str]:
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        data = json.load(f)
    items = {}
    if isinstance(data, dict):
        inner = data.get("items", data)
        if isinstance(inner, dict):
            for k, v in inner.items():
                items[k.strip().lower()] = v
    return items

def resolve_entity(name: str, entdict: Dict[str, List[Dict[str, Any]]], cutoff=0.8) -> List[Dict[str, Any]]:
    key = name.strip().lower()
    if key in entdict:
        return entdict[key]
    candidates = difflib.get_close_matches(key, entdict.keys(), n=5, cutoff=cutoff)
    res = []
    for c in candidates:
        res.extend(entdict[c])
    return res

def expand_slash_variants(name: str) -> List[str]:
    if "/" in name:
        parts = [p.strip() for p in name.split("/") if p.strip()]
        return parts
    return [name]

def normalize_item_name(name: str) -> List[str]:
    """Normalize item name and handle compound items like 'Spade Chisel'."""
    k = name.strip().lower()
    # Strip articles, quantities, and inventory slots
    k = re.sub(r"^(the|a|an)\s+", "", k, re.I)
    k = re.sub(r"^\d+x?\s*", "", k)  # e.g., '3x Logs' -> 'Logs'
    k = re.sub(r"\s*\(\d+\s+inventory\s+slots?\)", "", k, re.I)  # e.g., '(8 Inventory slots)'
    k = re.sub(r"\(.*?\)", "", k).strip()  # Other parentheses
    # Handle plural forms
    if k.endswith("s"):
        k = k[:-1]  # Remove trailing 's'
    # Split compound items (e.g., "Spade Chisel" -> ["Spade", "Chisel"])
    if k.lower() in ["spade chisel", "jug bowl"]:
        return [part.strip().title() for part in k.split(" ") if part.strip()]
    return [k.title()]

def resolve_item(name: str, itemdict: Dict[str, str], cutoff=0.6) -> List[Tuple[str, str]]:
    """Resolve item name to one or more (query, id) tuples, handling compounds."""
    normalized_names = normalize_item_name(name)
    results = []
    for norm_name in normalized_names:
        norm_lower = norm_name.lower()
        # Direct match first
        if norm_lower in itemdict:
            results.append((name, itemdict[norm_lower]))
            continue
        # Special handling for "Treasure Scroll"
        if "treasure scroll" in norm_lower:
            candidates = difflib.get_close_matches("clue scroll (beginner)", itemdict.keys(), n=1, cutoff=cutoff)
            if candidates:
                results.append((name, itemdict[candidates[0]]))
        else:
            # Fuzzy match for other items
            cand = difflib.get_close_matches(norm_lower, itemdict.keys(), n=1, cutoff=cutoff)
            if cand:
                results.append((name, itemdict[cand[0]]))
    return results

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--steps", required=True)
    ap.add_argument("--world", required=True)
    ap.add_argument("--items", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    steps = json.load(open(args.steps, "r", encoding="utf-8"))
    npcdict = load_entities(args.world, "npcs")
    objectdict = load_entities(args.world, "objects")
    itemdict = load_items(args.items)

    for s in steps:
        s["npc_matches"] = []
        s["object_matches"] = []
        s["item_matches"] = []
        # NPCs
        for name in s.get("npc_names", []):
            for n in expand_slash_variants(name):
                matches = resolve_entity(n, npcdict)
                if matches:
                    for m in matches:
                        s["npc_matches"].append({
                            "query": n,
                            "name": m.get("name"),
                            "id": m.get("id"),
                            "worldpoints": m.get("worldpoints"),
                        })
        # Objects
        for name in s.get("object_names", []):
            for n in expand_slash_variants(name):
                matches = resolve_entity(n, objectdict)
                if matches:
                    for m in matches:
                        s["object_matches"].append({
                            "query": n,
                            "name": m.get("name"),
                            "id": m.get("id"),
                            "worldpoints": m.get("worldpoints"),
                        })
        # Items
        for item in s.get("items", []):
            matches = resolve_item(item, itemdict)
            for query, item_id in matches:
                s["item_matches"].append({
                    "query": query,
                    "item_id": item_id
                })
        # Set resolved fields for generator
        if s["npc_matches"]:
            m = s["npc_matches"][0]
            s["npc_name_resolved"] = m["name"]
            s["npc_id"] = m["id"]
            s["npc_id_const"] = const_case(m["name"])
            if m["worldpoints"]:
                s["worldpoint"] = m["worldpoints"][0]
        if s["object_matches"]:
            m = s["object_matches"][0]
            s["object_name_resolved"] = m["name"]
            s["object_id"] = m["id"]
            s["object_id_const"] = const_case(m["name"])
            if m["worldpoints"]:
                s["worldpoint"] = m["worldpoints"][0]
        if s["item_matches"]:
            s["items_required"] = [m["query"] for m in s["item_matches"]]

    with open(args.out, "w", encoding="utf-8") as w:
        json.dump(steps, w, ensure_ascii=False, indent=2)
    print(f"Enriched {len(steps)} steps -> {args.out}")

if __name__ == "__main__":
    main()