#!/usr/bin/env python3
"""
generate_java.py
Generates Java code for quest helper plugin, using only ### headers as panels, preferring unpoisoned item IDs,
and generating unique, descriptive step field names with NPC/object names.
"""
import json
import argparse
import re
import sys
from collections import defaultdict

HEADER_IMPORTS = """package com.questhelper.helpers.playerguide;

import net.runelite.api.ItemID;
import net.runelite.api.NpcID;
import net.runelite.api.ObjectID;
import net.runelite.api.coords.WorldPoint;
import com.questhelper.BasicQuestHelper;
import com.questhelper.QuestStep;
import com.questhelper.steps.*;
import com.questhelper.requirements.*;
import com.questhelper.requirements.item.ItemRequirement;
import com.questhelper.requirements.item.ItemRequirements;
import com.questhelper.panel.PanelDetails;
import com.questhelper.requirements.util.*;
import com.questhelper.ItemCollections;

import java.util.*;
"""

def to_java_identifier(step: dict, idx: int) -> str:
    step_type = step.get("type", "unknown")
    instruction = step.get("instruction", step.get("raw", f"step{idx}")).lower()
    # Map step types to short prefixes
    type_prefixes = {
        "npc_interaction": "npc",
        "object_interaction": "obj",
        "item_action": "item",
        "movement": "move",
        "bank": "bank",
        "instruction": "note",
        "unknown": "step"
    }
    prefix = type_prefixes.get(step_type, "step")
    
    # Use resolved NPC or object name if available
    name = None
    if step_type == "npc_interaction" and step.get("npc_name_resolved"):
        name = step["npc_name_resolved"].lower()
    elif step_type in ("object_interaction", "bank") and step.get("object_name_resolved"):
        name = step["object_name_resolved"].lower()
    else:
        # Extract key action or item from instruction
        # Prioritize verbs or items from instruction
        verbs = [
            "talk", "speak", "trade", "pickpocket", "attack", "kill",
            "climb", "enter", "open", "close", "search", "fill", "empty",
            "use", "click", "examine", "chop", "mine", "fish", "catch",
            "pick", "take", "collect", "obtain", "get", "buy", "purchase",
            "sell", "equip", "wear", "wield", "drop", "destroy",
            "go", "head", "move", "walk", "run", "travel", "teleport",
            "bank", "withdraw", "deposit"
        ]
        for verb in verbs:
            if verb in instruction:
                name = verb
                break
        else:
            # Fallback to first few words of instruction
            name = " ".join(instruction.split()[:3])

    # Sanitize name: keep alphanumeric, spaces, and hyphens
    name = re.sub(r"[^a-z0-9\s\-]", "", name.strip())
    # Replace spaces and hyphens with underscores
    name = re.sub(r"[\s\-]+", "_", name)
    # Truncate to avoid overly long names (max 30 chars for name part)
    name = name[:30]
    # Combine prefix, name, and index
    identifier = f"{prefix}_{name}_{idx}"
    # Ensure valid Java identifier
    if not identifier or not identifier[0].isalpha():
        identifier = f"step_{idx}"
    # Avoid duplicates by checking existing identifiers
    return identifier

def const_case(name: str) -> str:
    return re.sub(r"[^A-Z0-9_]", "", name.strip().upper().replace(" ", "_").replace("-", "_").replace("'", ""))

def generate_java(steps, classname):
    panels = defaultdict(list)
    item_req_dict = {}
    step_fields = []
    step_defs = []
    panel_defs = []
    warnings = []
    seen_identifiers = set()

    # Valid panel names from ### headers
    valid_panels = {"Starting out", "Bank 1"}

    # Group by panel_name and collect item_matches
    for idx, step in enumerate(steps):
        panel = step.get("panel_name", "General")
        if panel not in valid_panels:
            panel = "General"
        panels[panel].append((idx, step))
        for m in step.get("item_matches", []):
            item_id = m.get("item_id")
            if not item_id or not str(item_id).isdigit():
                continue
            key = item_id
            canonical = m.get("canonical_name", m["query"])
            qty = m.get("quantity", 1)
            if key in item_req_dict:
                item_req_dict[key]["quantity"] = max(item_req_dict[key]["quantity"], qty)
            else:
                item_req_dict[key] = {"canonical": canonical, "quantity": qty, "id": item_id}

    # Build field declarations
    for idx, step in enumerate(steps):
        field_name = to_java_identifier(step, idx)
        # Ensure uniqueness
        base_name = field_name
        suffix = 0
        while field_name in seen_identifiers:
            suffix += 1
            field_name = f"{base_name}_{suffix}"
        seen_identifiers.add(field_name)
        step_fields.append(f"QuestStep {field_name};")

    # Build setupRequirements()
    req_lines = []
    item_vars = []
    seen_item_vars = set()
    for item in sorted(item_req_dict.values(), key=lambda x: x["canonical"]):
        canonical = item["canonical"]
        var = to_java_identifier({"type": "item", "instruction": canonical}, len(item_vars))
        # Ensure unique item variable names
        base_var = var
        suffix = 0
        while var in seen_item_vars:
            suffix += 1
            var = f"{base_var}_{suffix}"
        seen_item_vars.add(var)
        const = const_case(canonical)
        qty = item["quantity"]
        item_id = item["id"]
        if item_id and str(item_id).isdigit():
            if qty > 1:
                req_lines.append(f'{var} = new ItemRequirement("{canonical}", ItemID.{const}, {qty});')
            else:
                req_lines.append(f'{var} = new ItemRequirement("{canonical}", ItemID.{const});')
            item_vars.append(f"ItemRequirement {var};")
        else:
            warnings.append(f"Warning: Invalid or missing ItemID for '{canonical}'")

    # Build setupSteps()
    type_map = {
        "npc_interaction": "npc",
        "object_interaction": "object",
        "item_action": "detailed",
        "movement": "detailed",
        "bank": "object",
        "instruction": "detailed",
        "unknown": "detailed",
    }
    for idx, step in enumerate(steps):
        field_name = to_java_identifier(step, idx)
        if field_name in seen_identifiers:
            # Already handled uniqueness in field declarations
            pass
        stype = type_map.get(step.get("type", "unknown"), "detailed")
        desc = step.get("instruction", step.get("raw", ""))
        npc_id = step.get("npc_id_const")
        obj_id = step.get("object_id_const")
        wp = step.get("worldpoint")
        wp_str = "null"
        if wp and len(wp) == 3:
            wp_str = f"new WorldPoint({wp[0]}, {wp[1]}, {wp[2]})"
        if stype == "npc" and npc_id:
            try:
                npc_id_num = int(step.get("npc_id", ""))
                step_defs.append(f'{field_name} = new NpcStep(this, NpcID.{npc_id}, {wp_str}, "{desc}");')
                if step.get("dialogue_options"):
                    dlg = '", "'.join(map(str, step["dialogue_options"]))
                    step_defs.append(f'{field_name}.addDialogSteps("{dlg}");')
            except (ValueError, TypeError):
                warnings.append(f"Warning: Invalid NpcID for '{step.get('npc_name_resolved', 'unknown')}'")
                step_defs.append(f'{field_name} = new DetailedQuestStep(this, "{desc}");')
        elif stype == "object" and obj_id:
            try:
                obj_id_num = int(step.get("object_id", ""))
                step_defs.append(f'{field_name} = new ObjectStep(this, ObjectID.{obj_id}, {wp_str}, "{desc}");')
            except (ValueError, TypeError):
                warnings.append(f"Warning: Invalid ObjectID for '{step.get('object_name_resolved', 'unknown')}'")
                step_defs.append(f'{field_name} = new DetailedQuestStep(this, "{desc}");')
        else:
            step_defs.append(f'{field_name} = new DetailedQuestStep(this, "{desc}");')

    # Build getPanels()
    for panel_name, plist in panels.items():
        flist = []
        for i, s in plist:
            field_name = to_java_identifier(s, i)
            if field_name in seen_identifiers:
                pass  # Already handled
            flist.append(field_name)
        joined = ", ".join(flist)
        panel_var = to_java_identifier({"type": "panel", "instruction": panel_name}, len(panel_defs))
        panel_defs.append(
            f'PanelDetails {panel_var} = new PanelDetails("{panel_name}", Arrays.asList({joined}));'
        )
        panel_defs.append(f'panels.add({panel_var});')

    java_parts = []
    java_parts.append(HEADER_IMPORTS)
    java_parts.append(f"public class {classname} extends BasicQuestHelper" + " {\n")
    java_parts.append("    // === Step Fields ===\n    " + "\n    ".join(step_fields) + "\n")
    if item_req_dict:
        java_parts.append(
            "    // === Item Requirements ===\n    "
            + "\n    ".join(item_vars)
            + "\n"
        )
    java_parts.append(
        "    @Override\n    public Map<Integer, QuestStep> loadSteps()\n    {\n        Map<Integer, QuestStep> steps = new HashMap<>();\n        int idx = 0;\n"
    )
    for idx, step in enumerate(steps):
        field_name = to_java_identifier(step, idx)
        if field_name in seen_identifiers:
            pass  # Already handled
        java_parts.append(f"        steps.put(idx++, {field_name});")
    java_parts.append("\n        return steps;\n    }\n")
    java_parts.append("    @Override\n    public void setupRequirements()\n    {\n")
    for line in req_lines:
        java_parts.append(f"        {line}")
    java_parts.append("    }\n")
    java_parts.append("    @Override\n    public void setupZones()\n    {\n        // Define zones if needed\n    }\n")
    java_parts.append("    @Override\n    public void setupConditions()\n    {\n        // Define conditions if needed\n    }\n")
    java_parts.append("    @Override\n    public void setupSteps()\n    {\n")
    for line in step_defs:
        java_parts.append(f"        {line}")
    java_parts.append("    }\n")
    java_parts.append("    @Override\n    public List<PanelDetails> getPanels()\n    {\n        List<PanelDetails> panels = new ArrayList<>();\n")
    for line in panel_defs:
        java_parts.append("        " + line)
    java_parts.append("        return panels;\n    }\n")
    java_parts.append("}\n")
    java_code = "\n".join(java_parts)

    if warnings:
        for w in warnings:
            print(w, file=sys.stderr)

    return java_code

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="infile", required=True)
    ap.add_argument("--classname", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    steps = json.load(open(args.infile, "r", encoding="utf-8"))
    java_code = generate_java(steps, args.classname)
    with open(args.out, "w", encoding="utf-8") as f:
        f.write(java_code)
    print(f"Wrote Java to {args.out}")