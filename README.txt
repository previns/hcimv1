Make sure you git clone a fresh copy of quest_helper_master and runelite for most up to date data.

//git clone https://github.com/Zoinkwiz/quest-helper
//git clone https://github.com/runelite/runelite

Step 1. Paste wiki source code into wiki.txt and run cleanwiki.py - Check the file wiki_cleaned.txt to make sure wiki syntax is cleaned.
Step 2. Run worldpointscraper.py - The console log should tell you if there are any IDs missing.
Step 3. Run cleanQHDatabase.py - Will give you 2 files that are clean worldpoints linked to NPC and Object ids.
Step 4. Run run_all.py - Will attempt to generate a clean java file. Probably very jank atm

# Quest Helper Conversion Pipeline

This folder contains a 3-step pipeline to turn `wiki_cleaned.txt` into a Java skeleton quest helper file.

## Files
- `parse_steps.py`: parses and classifies each line into a structured JSON (`steps_parsed.json`).
- `resolve_entities.py`: looks up NPC/worldpoints (from `worldpoints.json`) and items (from `OSRS ID List.json`) to enrich steps (`steps_enriched.json`).
- `generate_java.py`: converts the enriched JSON into a Java class (`QuestFromWiki.java`).
- `run_all.py`: convenience script to run the full pipeline.
- `wiki_cleaned.txt`, `worldpoints.json`, `OSRS ID List.json`: your input files (already placed here).

## Quick Start
```bash
python run_all.py
```

### Or run step-by-step
```bash
python parse_steps.py --in wiki_cleaned.txt --out steps_parsed.json
python resolve_entities.py --steps steps_parsed.json --world worldpoints.json --items "OSRS ID List.json" --out steps_enriched.json
python generate_java.py --in steps_enriched.json --classname QuestFromWiki --out QuestFromWiki.java
```

## Notes & Limitations
- The parser uses heuristics (regex + keyword rules). It won’t be 100% accurate on the first pass. You can refine keyword lists in `parse_steps.py` without touching the other scripts.
- `resolve_entities.py`:
  - Tries exact match first, then fuzzy matching for NPCs and items.
  - If a line says "man/woman", both will be queried; multiple matches are appended (the Java generator currently picks the first match per line—tweak as needed).
- `generate_java.py` emits a **generic** Java class with placeholder Step containers. Replace with your plugin’s real step classes/methods.
- Dialogue options like `(3,1)` are detected and passed to Java as `int[]`.

## Where to tweak
- Add/adjust patterns in `STEP_KEYWORDS` inside `parse_steps.py` to improve classification.
- In `resolve_entities.py`, adapt `load_worldpoints()` if your JSON shape differs.
- In `generate_java.py`, swap the placeholder Step structure with your actual quest helper API.