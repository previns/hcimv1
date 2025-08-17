#!/usr/bin/env python3
"""
run_all.py
Convenience script to run the full quest helper conversion pipeline.
"""
import subprocess
import os

def run_command(command):
    print(f"Running: {' '.join(command)}")
    try:
        result = subprocess.run(command, check=True, text=True, capture_output=True)
        print(result.stdout, end='')
        if result.stderr:
            print(result.stderr, end='')
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}", file=sys.stderr)
        print(e.stderr, file=sys.stderr)
        raise

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    parse_steps = [
        "python", os.path.join(base_dir, "parse_steps.py"),
        "--in", os.path.join(base_dir, "wiki_cleaned.txt"),
        "--out", os.path.join(base_dir, "steps_parsed.json")
    ]
    resolve_entities = [
        "python", os.path.join(base_dir, "resolve_entities.py"),
        "--steps", os.path.join(base_dir, "steps_parsed.json"),
        "--world", os.path.join(base_dir, "worldpoints.json"),
        "--items", os.path.join(base_dir, "OSRS ID List.json"),
        "--out", os.path.join(base_dir, "steps_enriched.json")
    ]
    generate_java = [
        "python", os.path.join(base_dir, "generate_java.py"),
        "--in", os.path.join(base_dir, "steps_enriched.json"),
        "--classname", "QuestFromWiki",
        "--out", os.path.join(base_dir, "QuestFromWiki.java")
    ]

    run_command(parse_steps)
    run_command(resolve_entities)
    run_command(generate_java)

if __name__ == "__main__":
    main()