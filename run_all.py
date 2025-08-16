#!/usr/bin/env python3
"""
run_all.py
One-shot runner for the whole pipeline using files placed in the same folder.
"""
import subprocess, sys, os, json, shutil
from pathlib import Path

base = Path(__file__).parent
wiki = base/"wiki_cleaned.txt"
world = base/"worldpoints.json"
items = base/"OSRS ID List.json"

parsed = base/"steps_parsed.json"
enriched = base/"steps_enriched.json"
java_out = base/"QuestFromWiki.java"

cmds = [
    [sys.executable, str(base/"parse_steps.py"), "--in", str(wiki), "--out", str(parsed)],
    [sys.executable, str(base/"resolve_entities.py"), "--steps", str(parsed), "--world", str(world), "--items", str(items), "--out", str(enriched)],
    [sys.executable, str(base/"generate_java.py"), "--in", str(enriched), "--classname", "QuestFromWiki", "--out", str(java_out)],
]

for c in cmds:
    print("Running:", " ".join(c))
    subprocess.check_call(c)

print("Done. Outputs:")
print("  -", parsed)
print("  -", enriched)
print("  -", java_out)