#!/usr/bin/env python3
"""
generate_java.py
Generates a Runelite QuestHelper Java class from enriched steps JSON.
Handles ObjectStep for items obtained from objects.
Uses Path(__file__).parent for output path.
"""
import json
import argparse
import re
from pathlib import Path
from typing import Dict, List, Any

def const_case(name: str) -> str:
    return re.sub(r"[^A-Z0-9_]", "", name.upper().replace(" ", "_").replace("-", "_").replace("'", ""))

def generate_java(steps: List[Dict[str, Any]], classname: str, out_path: str):
    imports = [
        "package com.questhelper.helpers.playerguide;",
        "",
        "import net.runelite.api.ItemID;",
        "import net.runelite.api.NpcID;",
        "import net.runelite.api.ObjectID;",
        "import net.runelite.api.coords.WorldPoint;",
        "import com.questhelper.BasicQuestHelper;",
        "import com.questhelper.QuestStep;",
        "import com.questhelper.steps.*;",
        "import com.questhelper.requirements.*;",
        "import com.questhelper.requirements.item.ItemRequirement;",
        "import com.questhelper.requirements.item.ItemRequirements;",
        "import com.questhelper.panel.PanelDetails;",
        "import com.questhelper.requirements.util.*;",
        "import com.questhelper.ItemCollections;",
        "import java.util.*;"
    ]

    # Collect unique items for requirements
    items = {}
    for step in steps:
        for item in step.get("item_matches", []):
            canonical = item["canonical_name"]
            item_id = item["item_id"]
            quantity = item["quantity"]
            var_name = canonical.lower().replace(" ", "_").replace("'", "")
            if quantity > 1:
                var_name += f"_{quantity}x"
            items[var_name] = {"name": canonical, "id": item_id, "quantity": quantity}

    # Generate class
    class_lines = [f"public class {classname} extends BasicQuestHelper {{"]

    # Item requirements
    class_lines.append("    // Item Requirements")
    for var_name, item in items.items():
        class_lines.append(f"    ItemRequirement {var_name};")

    # Step fields
    class_lines.append("\n    // Step Fields")
    for idx, step in enumerate(steps):
        step_name = step["instruction"].lower().replace(" ", "_").replace("[[", "").replace("]]", "").replace("(", "").replace(")", "").replace("&", "and")
        step_name = re.sub(r"[^a-z0-9_]", "", step_name)
        step_name = f"step_{step_name}_{idx}"
        class_lines.append(f"    QuestStep {step_name};")

    # setupRequirements
    class_lines.append("\n    @Override")
    class_lines.append("    public void setupRequirements()")
    class_lines.append("    {")
    for var_name, item in items.items():
        if item["id"].startswith("ItemCollections."):
            class_lines.append(f"        {var_name} = new ItemRequirement(\"{item['name']}\", {item['id']}, {item['quantity']});")
        else:
            class_lines.append(f"        {var_name} = new ItemRequirement(\"{item['name']}\", ItemID.{const_case(item['name'])}, {item['quantity']});")
    class_lines.append("    }")

    # setupSteps
    class_lines.append("\n    @Override")
    class_lines.append("    public void setupSteps()")
    class_lines.append("    {")
    for idx, step in enumerate(steps):
        step_name = step["instruction"].lower().replace(" ", "_").replace("[[", "").replace("]]", "").replace("(", "").replace(")", "").replace("&", "and")
        step_name = re.sub(r"[^a-z0-9_]", "", step_name)
        step_name = f"step_{step_name}_{idx}"
        step_type = step.get("type", "DetailedQuestStep")
        instruction = step["instruction"].replace('"', '\\"')

        if step_type == "NpcStep":
            npc_id = step.get("npc_id", "0")
            npc_const = step.get("npc_id_const", "UNKNOWN")
            worldpoint = step.get("worldpoint", None)
            comment = step.get("comment", None)
            if comment:
                class_lines.append(f"        // {comment}")
            wp_str = "null" if worldpoint is None else f"new WorldPoint({worldpoint[0][0]}, {worldpoint[0][1]}, {worldpoint[0][2]})"
            class_lines.append(f"        {step_name} = new NpcStep(this, NpcID.{npc_const}_{npc_id}, {wp_str}, \"{instruction}\");")
            if step.get("dialogue_options"):
                dialog = ", ".join(f"\"{d}\"" for d in step["dialogue_options"])
                class_lines.append(f"        {step_name}.addDialogSteps({dialog});")
        elif step_type == "ObjectStep":
            obj_id = step.get("object_id", "0")
            obj_const = step.get("object_id_const", "UNKNOWN")
            worldpoint = step.get("worldpoint", None)
            comment = step.get("comment", None)
            if comment:
                class_lines.append(f"        // {comment}")
            wp_str = "null" if worldpoint is None else f"new WorldPoint({worldpoint[0][0]}, {worldpoint[0][1]}, {worldpoint[0][2]})"
            class_lines.append(f"        {step_name} = new ObjectStep(this, ObjectID.{obj_const}_{obj_id}, {wp_str}, \"{instruction}\");")
            # Add item requirements for ObjectStep
            for item in step.get("item_matches", []):
                var_name = item["canonical_name"].lower().replace(" ", "_").replace("'", "")
                if item["quantity"] > 1:
                    var_name += f"_{item['quantity']}x"
                class_lines.append(f"        {step_name}.addItemRequirements({var_name});")
        else:
            class_lines.append(f"        {step_name} = new DetailedQuestStep(this, \"{instruction}\");")
    class_lines.append("    }")

    # loadSteps
    class_lines.append("\n    @Override")
    class_lines.append("    public Map<Integer, QuestStep> loadSteps()")
    class_lines.append("    {")
    class_lines.append("        Map<Integer, QuestStep> steps = new HashMap<>();")
    class_lines.append("        int idx = 0;")
    for idx, step in enumerate(steps):
        step_name = step["instruction"].lower().replace(" ", "_").replace("[[", "").replace("]]", "").replace("(", "").replace(")", "").replace("&", "and")
        step_name = re.sub(r"[^a-z0-9_]", "", step_name)
        step_name = f"step_{step_name}_{idx}"
        class_lines.append(f"        steps.put(idx++, {step_name});")
    class_lines.append("        return steps;")
    class_lines.append("    }")

    # getPanels
    class_lines.append("\n    @Override")
    class_lines.append("    public List<PanelDetails> getPanels()")
    class_lines.append("    {")
    class_lines.append("        List<PanelDetails> panels = new ArrayList<>();")
    panels = {}
    for idx, step in enumerate(steps):
        panel_name = step.get("panel_name", "General")
        step_name = step["instruction"].lower().replace(" ", "_").replace("[[", "").replace("]]", "").replace("(", "").replace(")", "").replace("&", "and")
        step_name = re.sub(r"[^a-z0-9_]", "", step_name)
        step_name = f"step_{step_name}_{idx}"
        if panel_name not in panels:
            panels[panel_name] = []
        panels[panel_name].append(step_name)
    for panel_name, step_names in panels.items():
        step_list = ", ".join(step_names)
        class_lines.append(f"        PanelDetails panel_{panel_name.lower().replace(' ', '_')} = new PanelDetails(\"{panel_name}\", Arrays.asList({step_list}));")
        class_lines.append(f"        panels.add(panel_{panel_name.lower().replace(' ', '_')});")
    class_lines.append("        return panels;")
    class_lines.append("    }")

    # Empty setupZones and setupConditions
    class_lines.append("\n    @Override")
    class_lines.append("    public void setupZones()")
    class_lines.append("    {")
    class_lines.append("        // Define zones if needed")
    class_lines.append("    }")
    class_lines.append("\n    @Override")
    class_lines.append("    public void setupConditions()")
    class_lines.append("    {")
    class_lines.append("        // Define conditions if needed")
    class_lines.append("    }")
    class_lines.append("}")

    # Write to file
    out_path = Path(out_path)
    with out_path.open("w", encoding="utf-8") as f:
        f.write("\n".join(imports + [""] + class_lines))
    print(f"Wrote Java to {out_path}")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", required=True, dest="input")
    ap.add_argument("--classname", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    input_path = Path(args.input)
    try:
        with input_path.open("r", encoding="utf-8") as f:
            steps = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error: Failed to parse {input_path}: {e}", file=sys.stderr)
        raise
    except FileNotFoundError:
        print(f"Error: {input_path} not found", file=sys.stderr)
        raise

    generate_java(steps, args.classname, args.out)

if __name__ == "__main__":
    main()