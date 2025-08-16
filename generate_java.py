#!/usr/bin/env python3
"""
generate_java.py
Fixed version with improvements:
- Map step type to Java stype (npc, object, detailed)
- Pull npc_id_const, object_id_const, worldpoint from step resolved fields
- Use step["instruction"] for desc
- Use step["panel_name"] for grouping panels
- Collect item_requirements from all step["items_required"]
- Add dialogue if present
- Fallback to DetailedQuestStep
- Updated imports if needed
- Use Arrays.asList for panels
- Skip invalid ItemID/ObjectID constants with warning
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

def to_java_identifier(name):
    name = re.sub(r"[^a-zA-Z0-9_]", "", name.strip().lower())
    if not name:
        name = "step"
    return name

def const_case(name):
    return re.sub(r"[^A-Z0-9_]", "", name.strip().upper().replace(" ", "_").replace("-", "_").replace("'", ""))

def generate_java(steps, classname):
    panels = defaultdict(list)
    item_requirements = set()
    step_fields = []
    step_defs = []
    panel_defs = []
    warnings = []

    # Group by panel_name
    for idx, step in enumerate(steps):
        panel = step.get("panel_name", "General")
        panels[panel].append((idx, step))
        if step.get("items_required"):
            for item in step["items_required"]:
                item_requirements.add(item)

    # Build field declarations
    for idx, step in enumerate(steps):
        field_name = to_java_identifier(step.get("name", f"step{idx}"))
        step_fields.append(f"QuestStep {field_name};")

    # Build setupRequirements()
    req_lines = []
    for item in sorted(item_requirements):
        var = to_java_identifier(item)
        const = const_case(item)
        # Check if ItemID exists (heuristic: assume numeric ID means valid)
        try:
            # Find the item_id from item_matches
            item_id = None
            for match in step.get("item_matches", []):
                if match["query"] == item:
                    item_id = match["item_id"]
                    break
            if item_id and item_id.isdigit():
                req_lines.append(f'{var} = new ItemRequirement("{item}", ItemID.{const});')
            else:
                warnings.append(f"Warning: Invalid or missing ItemID for '{item}'")
        except (ValueError, IndexError, AttributeError):
            warnings.append(f"Warning: Invalid or missing ItemID for '{item}'")

    # Build setupSteps()
    type_map = {
        "npc_interaction": "npc",
        "object_interaction": "object",
        "item_action": "detailed",
        "movement": "detailed",
        "bank": "object",  # assume bank booth
        "instruction": "detailed",
        "unknown": "detailed",
    }
    for idx, step in enumerate(steps):
        field_name = to_java_identifier(step.get("name", f"step{idx}"))
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
                # Verify NPC ID is numeric
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
                # Verify Object ID is numeric
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
            flist.append(to_java_identifier(s.get("name", f"step{i}")))
        joined = ", ".join(flist)
        panel_var = to_java_identifier(panel_name) + "Panel"
        panel_defs.append(
            f'PanelDetails {panel_var} = new PanelDetails("{panel_name}", Arrays.asList({joined}));'
        )
        panel_defs.append(f'panels.add({panel_var});')

    java_parts = []

    java_parts.append(HEADER_IMPORTS)
    java_parts.append(f"public class {classname} extends BasicQuestHelper" + " {\n")
    java_parts.append("    // === Step Fields ===\n    " + "\n    ".join(step_fields) + "\n")
    if item_requirements:
        java_parts.append(
            "    // === Item Requirements ===\n    "
            + "\n    ".join(f"ItemRequirement {to_java_identifier(item)};" for item in sorted(item_requirements))
            + "\n"
        )

    # loadSteps()
    java_parts.append(
        "    @Override\n    public Map<Integer, QuestStep> loadSteps()\n    {\n        Map<Integer, QuestStep> steps = new HashMap<>();\n        int idx = 0;\n"
    )
    for idx, step in enumerate(steps):
        field_name = to_java_identifier(step.get("name", f"step{idx}"))
        java_parts.append(f"        steps.put(idx++, {field_name});")
    java_parts.append("\n        return steps;\n    }\n")

    # setupRequirements()
    java_parts.append("    @Override\n    public void setupRequirements()\n    {\n")
    for line in req_lines:
        java_parts.append(f"        {line}")
    java_parts.append("    }\n")

    # setupZones()
    java_parts.append("    @Override\n    public void setupZones()\n    {\n        // Define zones if needed\n    }\n")

    # setupConditions()
    java_parts.append("    @Override\n    public void setupConditions()\n    {\n        // Define conditions if needed\n    }\n")

    # setupSteps()
    java_parts.append("    @Override\n    public void setupSteps()\n    {\n")
    for line in step_defs:
        java_parts.append(f"        {line}")
    java_parts.append("    }\n")

    # getPanels()
    java_parts.append("    @Override\n    public List<PanelDetails> getPanels()\n    {\n        List<PanelDetails> panels = new ArrayList<>();\n")
    for line in panel_defs:
        java_parts.append("        " + line)
    java_parts.append("        return panels;\n    }\n")

    java_parts.append("}\n")
    java_code = "\n".join(java_parts)

    # Write warnings to stderr
    if warnings:
        for w in warnings:
            print(w, file=sys.stderr)

    return java_code

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--infile", required=True)
    ap.add_argument("--classname", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    steps = json.load(open(args.infile, "r", encoding="utf-8"))
    java_code = generate_java(steps, args.classname)
    with open(args.out, "w", encoding="utf-8") as f:
        f.write(java_code)
    print(f"Wrote Java to {args.out}")