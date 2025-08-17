#!/usr/bin/env python3
"""
parse_steps.py
Parses wiki text into structured JSON steps for quest helper conversion.
Ensures accurate item, NPC, and object extraction for ObjectStep interactions.
Uses Path(__file__).parent for input/output paths.
Enhanced [DEBUG] logging to diagnose early failures.
Uses latin1 encoding to avoid chardet dependency.
"""
import re
import json
import argparse
import sys
from typing import Dict, List, Any
from pathlib import Path

def parse_wiki_text(wiki_text: str) -> List[Dict[str, Any]]:
    print("[DEBUG] Entering parse_wiki_text")
    steps = []
    try:
        lines = wiki_text.split("\n")
        print(f"[DEBUG] Split input into {len(lines)} lines")
        for idx, line in enumerate(lines):
            print(f"[DEBUG] Processing line {idx}: {line}")
            try:
                line = line.strip()
                if not line or not line.startswith("*"):
                    print(f"[DEBUG] Skipping line {idx}: empty or not a step")
                    continue

                step = {
                    "raw": line[1:].strip(),
                    "instruction": line[1:].strip(),
                    "index": idx,
                    "npc_names": [],
                    "object_names": [],
                    "items": [],
                    "dialogue_options": [],
                    "type": "DetailedQuestStep",
                    "panel_name": "General"
                }
                print(f"[DEBUG] Initialized step for index {idx}: {step['raw']}")

                # Extract NPCs with optional dialogue options (e.g., (3,1))
                try:
                    npc_matches = re.findall(r"\[\[([^\]\|]+)(?:\|[^\]]*)?\]\](?:\s*\((\d+,\d+)\))?", line)
                    print(f"[DEBUG] NPC matches for line {idx}: {npc_matches}")
                    for npc, dialog in npc_matches:
                        npc = npc.strip()
                        step["npc_names"].append(npc)
                        if dialog:
                            step["dialogue_options"] = [d.strip() for d in dialog.split(",")]
                            print(f"[DEBUG] Added dialogue options for NPC '{npc}': {step['dialogue_options']}")
                        step["type"] = "NpcStep"
                        print(f"[DEBUG] Set step type to NpcStep for NPC '{npc}'")
                except Exception as e:
                    print(f"[DEBUG] Error extracting NPCs for line {idx}: {e}", file=sys.stderr)

                # Extract items (e.g., [[Bronze Dagger]], 3x Logs, Forestry Kit, or Leather Gloves on the table)
                try:
                    item_matches = re.findall(r"\[\[([^\]\|]+)(?:\|[^\]]*)?\]\](?:\((\d+)\))?|(\d+x)\s+([^\[\]\(\),;&]+(?:\s+[^\[\]\(\),;&]+)*)|([^\[\]\(\),;&]+(?:\s+[^\[\]\(\),;&]+)*)\s+(?:on|off|in|at)\s+(?:the|a)\s+([^\[\]\(\),;&]+)", line)
                    print(f"[DEBUG] Item matches for line {idx}: {item_matches}")
                    for match in item_matches:
                        if match[0]:  # [[Item]] format
                            item, qty = match[0].strip(), match[1]
                            step["items"].append({"name": item, "quantity": int(qty) if qty else 1})
                            print(f"[DEBUG] Added item from [[Item]]: {item}, quantity: {qty or 1}")
                        elif match[2]:  # Nx Item format
                            qty, item = match[2].strip(), match[3].strip()
                            step["items"].append({"name": item, "quantity": int(qty[:-1]) if qty else 1})
                            print(f"[DEBUG] Added item from Nx format: {item}, quantity: {qty[:-1] or 1}")
                        elif match[4]:  # Item on/off/in/at Object (e.g., Leather Gloves on the table)
                            item, obj = match[4].strip(), match[5].strip()
                            step["items"].append({"name": item, "quantity": 1})
                            print(f"[DEBUG] Added item from ObjectStep: {item}, object: {obj}")
                            if obj not in {"the", "your", "lumbridge", "draynor", "kitchen", "house", "top", "floor"}:
                                step["object_names"].append(obj.title())
                                step["type"] = "ObjectStep"
                                print(f"[DEBUG] Set step type to ObjectStep for object '{obj.title()}'")
                except Exception as e:
                    print(f"[DEBUG] Error extracting items for line {idx}: {e}", file=sys.stderr)

                # Extract standalone objects (e.g., "fill the jug on the sink")
                try:
                    object_words = ["on", "at", "in", "fill", "use", "take", "off"]
                    for word in object_words:
                        if f" {word} " in line.lower() and not any(match[4] for match in item_matches):  # Avoid duplicating objects
                            parts = line.lower().split(f" {word} ")
                            if len(parts) > 1:
                                obj = parts[1].split(" ")[0].strip()
                                if obj and obj not in {"the", "your", "lumbridge", "draynor", "kitchen", "house", "top", "floor"}:
                                    step["object_names"].append(obj.title())
                                    step["type"] = "ObjectStep"
                                    print(f"[DEBUG] Added standalone object '{obj.title()}' and set type to ObjectStep")
                except Exception as e:
                    print(f"[DEBUG] Error extracting standalone objects for line {idx}: {e}", file=sys.stderr)

                # Set panel name and override step type for specific cases
                try:
                    if any(kw in line.lower() for kw in ["bank", "deposit", "withdraw"]):
                        step["type"] = "DetailedQuestStep"
                        step["panel_name"] = "Bank 1"
                        print(f"[DEBUG] Set type to DetailedQuestStep and panel to 'Bank 1' due to banking keywords")
                    elif any(kw in line.lower() for kw in ["head", "go", "move", "upstairs", "down", "basement"]):
                        step["type"] = "DetailedQuestStep"
                        step["panel_name"] = "Bank 1" if "bank" in line.lower() else "Starting out"
                        print(f"[DEBUG] Set type to DetailedQuestStep and panel to '{step['panel_name']}' due to movement keywords")
                    elif "kill" in line.lower():
                        step["type"] = "DetailedQuestStep"
                        step["panel_name"] = "Bank 1"
                        print(f"[DEBUG] Set type to DetailedQuestStep and panel to 'Bank 1' due to 'kill' keyword")
                    else:
                        step["panel_name"] = "Starting out"
                        print(f"[DEBUG] Set panel to 'Starting out'")
                except Exception as e:
                    print(f"[DEBUG] Error setting panel name for line {idx}: {e}", file=sys.stderr)

                # Filter out invalid items
                try:
                    invalid_items = {"", "x", "1", "2", "3", "restless ghost", "lumbridge easy diary", "tree gnome village", 
                                     "client of kourend + druidic ritual", "rune mysteries", "monk's friend", "x marks the spot"}
                    step["items"] = [item for item in step["items"] if item["name"].lower() not in invalid_items 
                                     and not any(npc.lower() in item["name"].lower() for npc in step["npc_names"])]
                    print(f"[DEBUG] Filtered items for step {idx}: {step['items']}")
                except Exception as e:
                    print(f"[DEBUG] Error filtering items for line {idx}: {e}", file=sys.stderr)

                steps.append(step)
                print(f"[DEBUG] Appended step {idx}: {step}")
            except Exception as e:
                print(f"[DEBUG] Error processing line {idx}: {e}", file=sys.stderr)
                continue
    except Exception as e:
        print(f"[DEBUG] Error in parse_wiki_text: {e}", file=sys.stderr)
        raise
    finally:
        print(f"[DEBUG] Finished parse_wiki_text, total steps: {len(steps)}")

    return steps

def main():
    print("[DEBUG] Starting main function")
    try:
        print("[DEBUG] Initializing ArgumentParser")
        ap = argparse.ArgumentParser()
        ap.add_argument("--in", required=True, dest="input")
        ap.add_argument("--out", required=True)
        args = ap.parse_args()
        print(f"[DEBUG] Parsed arguments: input={args.input}, out={args.out}")

        input_path = Path(args.input)
        output_path = Path(args.out)
        print(f"[DEBUG] Input path: {input_path}, Output path: {output_path}")

        # Check if input file exists
        print(f"[DEBUG] Checking if input file exists: {input_path}")
        if not input_path.exists():
            print(f"[DEBUG] Error: Input file {input_path} does not exist", file=sys.stderr)
            raise FileNotFoundError(f"Input file {input_path} does not exist")
        if not input_path.is_file():
            print(f"[DEBUG] Error: Input path {input_path} is not a file", file=sys.stderr)
            raise IsADirectoryError(f"Input path {input_path} is not a file")

        # Read input file with latin1 encoding
        print(f"[DEBUG] Reading input file: {input_path}")
        try:
            wiki_text = input_path.read_text(encoding="latin1")
            print(f"[DEBUG] Successfully read input file with latin1, length: {len(wiki_text)} characters")
        except Exception as e:
            print(f"[DEBUG] Error reading input file: {e}", file=sys.stderr)
            raise

        steps = parse_wiki_text(wiki_text)
        print(f"[DEBUG] Writing output to: {output_path}")
        try:
            with output_path.open("w", encoding="utf-8") as f:
                json.dump(steps, f, indent=2, ensure_ascii=False)
            print(f"Parsed {len(steps)} steps -> {output_path}")
            print(f"[DEBUG] Successfully wrote output to {output_path}")
        except Exception as e:
            print(f"[DEBUG] Error writing output file: {e}", file=sys.stderr)
            raise

    except Exception as e:
        print(f"[DEBUG] Unexpected error in main: {e}", file=sys.stderr)
        raise

if __name__ == "__main__":
    print("[DEBUG] Script execution started")
    main()
    print("[DEBUG] Script execution completed")