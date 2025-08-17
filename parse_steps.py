#!/usr/bin/env python3
"""
parse_steps.py
Reads a wiki_cleaned.txt and produces a structured JSON with best-effort step classification.
Usage:
  python parse_steps.py --in /path/wiki_cleaned.txt --out /path/steps_parsed.json
"""
import re
import json
import argparse
from typing import List, Dict, Any, Optional

STEP_KEYWORDS = {
    "npc_interaction": [
        r"^\*?\s*(talk to)\b",
        r"^\*?\s*(speak to)\b",
        r"^\*?\s*(trade with)\b",
        r"^\*?\s*(pickpocket)\b",
        r"^\*?\s*(attack)\b",
        r"^\*?\s*(kill)\b",
        r"^\*?\s*(start|begin)\s+the\s+quest\b",
    ],
    "object_interaction": [
        r"^\*?\s*(climb|enter|open|close|search|fill|empty|use on|click|examine|chop|mine|fish|catch|woodcut|hunt|thieve from|thieve)\b",
    ],
    "item_action": [
        r"^\*?\s*(pick up|take|collect|loot|obtain|get)\b",
        r"^\*?\s*(use)\b.*\bon\b",
        r"^\*?\s*(craft|cook|brew|smith|fletch|combine|mix)\b",
        r"^\*?\s*(withdraw|deposit)\b",
        r"^\*?\s*(buy|purchase|sell)\b",
        r"^\*?\s*(equip|wear|wield)\b",
        r"^\*?\s*(drop|destroy)\b",
    ],
    "movement": [
        r"^\*?\s*(go to|head to|move to|walk to|run to|travel to|teleport to|enter|climb|descend|ascend)\b",
    ],
    "bank": [
        r"^\*?\s*(bank:|open bank|use bank|withdraw|deposit)\b",
    ],
    "instruction": [
        r"^\*?\s*(note:|tip:|warning:|optional:)\b",
    ]
}

DIALOGUE_RE = re.compile(r"\(([\d,\s]+)\)")
NPC_WIKI_RE = re.compile(r"\[\[([^\[\]]+)\]\]")
QUEST_TAG_RE = re.compile(r"\[([^\[\]]+)\]\s*$")
CHOICE_SLASH_RE = re.compile(r"([A-Za-z][A-Za-z '\-]+)\s*/\s*([A-Za-z][A-Za-z '\-]+)")
CLEAN_RE = re.compile(r"\[\[.*?\]\]|\(\d.*?\)|\[.*?\]$")

def classify_line(line: str) -> str:
    l = line.strip().lower()
    for t, patterns in STEP_KEYWORDS.items():
        for p in patterns:
            if re.search(p, l):
                return t
    if NPC_WIKI_RE.search(line):
        return "npc_interaction"
    return "unknown"

def parse_dialogue(line: str) -> Optional[List[int]]:
    m = DIALOGUE_RE.search(line)
    if not m:
        return None
    nums = [s.strip() for s in m.group(1).split(",")]
    res = []
    for n in nums:
        try:
            res.append(int(n))
        except:
            pass
    return res or None

def parse_entity_names(line: str, verbs: List[str]) -> List[str]:
    names = []
    for m in NPC_WIKI_RE.finditer(line):
        names.append(m.group(1).strip())
    m = CHOICE_SLASH_RE.search(line)
    if m:
        a = m.group(1).strip().title()
        b = m.group(2).strip().title()
        if a not in names:
            names.append(a)
        if b not in names:
            names.append(b)
    for verb in verbs:
        rgx = re.compile(rf"\b{verb}\s+(a|an|the)?\s*([A-Za-z '\-]+)\b", re.IGNORECASE)
        m2 = rgx.search(line)
        if m2:
            cand = m2.group(2).strip().title()
            cand = cand.split("[")[0].strip()
            if cand and cand.lower() not in {"to"} and cand not in names:
                names.append(cand)
    return names

def parse_npc_names(line: str) -> List[str]:
    return parse_entity_names(line, ["talk to", "speak to", "trade with", "pickpocket", "attack", "kill"])

def parse_object_names(line: str) -> List[str]:
    names = parse_entity_names(line, ["climb", "enter", "open", "close", "search", "fill", "empty", "chop", "mine", "fish", "catch", "hunt", "thieve from", "thieve"])
    m = re.search(r"\bon the\s+([A-Za-z '\-]+)\b", line, re.I)
    if m:
        cand = m.group(1).strip().title()
        if cand not in names:
            names.append(cand)
    m2 = re.search(r"\bnext to the\s+([A-Za-z '\-]+)\b", line, re.I)
    if m2:
        cand = m2.group(1).strip().title()
        if cand not in names:
            names.append(cand)
    return names

def parse_items(line: str) -> List[Dict[str, Any]]:
    items = []
    for m in re.finditer(r'"([^"]+)"', line):
        item_name = m.group(1).strip()
        quantity = 1
        if re.match(r"^\d+x?\s", item_name):
            qty_match = re.match(r"^(\d+)x?\s*(.+)", item_name)
            if qty_match:
                quantity = int(qty_match.group(1))
                item_name = qty_match.group(2).strip()
        items.append({"name": item_name, "quantity": quantity})
    m = re.search(r"\buse\s+([ ^on]+?)\s+on\s+(.+)", line, re.I)
    if m:
        left = m.group(1).strip(" .,:;")
        right = m.group(2).strip(" .,:;")
        for item in [left, right]:
            quantity = 1
            if re.match(r"^\d+x?\s", item):
                qty_match = re.match(r"^(\d+)x?\s*(.+)", item)
                if qty_match:
                    quantity = int(qty_match.group(1))
                    item = qty_match.group(2).strip()
            items.append({"name": item, "quantity": quantity})
    m2 = re.search(r"\b(withdraw|deposit)\s*:\s*(.+)", line, re.I)
    if m2:
        payload = m2.group(2)
        for token in re.split(r"[,;/]| and ", payload):
            t = token.strip(" .")
            if t:
                quantity = 1
                if re.match(r"^\d+x?\s", t):
                    qty_match = re.match(r"^(\d+)x?\s*(.+)", t)
                    if qty_match:
                        quantity = int(qty_match.group(1))
                        t = qty_match.group(2).strip()
                items.append({"name": t, "quantity": quantity})
    for verb in ["pick up", "take", "collect", "obtain", "get", "buy", "purchase", "sell", "equip", "wear", "wield", "drop", "destroy"]:
        rgx = re.compile(rf"\b{verb}\s+([A-Za-z0-9 '\-()#]+)", re.I)
        m3 = rgx.search(line)
        if m3:
            cand = m3.group(1).split("[")[0].strip(" .")
            if cand:
                quantity = 1
                if re.match(r"^\d+x?\s", cand):
                    qty_match = re.match(r"^(\d+)x?\s*(.+)", cand)
                    if qty_match:
                        quantity = int(qty_match.group(1))
                        cand = qty_match.group(2).strip()
                items.append({"name": cand, "quantity": quantity})
    uniq = []
    seen = set()
    for item in items:
        name = re.sub(r"^(the|a|an)\s+", "", item["name"], re.I).strip()
        name = re.sub(r"\s*\(\d+\s+inventory\s+slots?\)", "", name, re.I).strip()
        name = re.sub(r"\(.*?\)", "", name).strip()
        subs = re.split(r"\s*\+\s*|\s+and\s+|&", name)
        for sub in subs:
            sub = sub.strip()
            if sub and len(sub) > 2 and sub.lower() not in {"the", "a", "an"} and sub not in seen:
                seen.add(sub)
                uniq.append({"name": sub, "quantity": item["quantity"]})
    return uniq

def parse_quest_tag(line: str) -> Optional[str]:
    m = QUEST_TAG_RE.search(line)
    if m:
        return m.group(1).strip()
    return None

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="infile", required=True)
    ap.add_argument("--out", dest="outfile", required=True)
    args = ap.parse_args()

    out: List[Dict[str, Any]] = []
    current_panel = "General"
    with open(args.infile, "r", encoding="utf-8", errors="ignore") as f:
        for lineno, raw in enumerate(f, start=1):
            line = raw.rstrip("\n")
            if not line.strip():
                continue
            if line.startswith("###"):
                current_panel = line.strip("# ").strip()
                continue
            step_type = classify_line(line)
            dialogue = parse_dialogue(line)
            npc_names = parse_npc_names(line) if step_type in ("npc_interaction", "unknown") else []
            object_names = parse_object_names(line) if step_type in ("object_interaction", "bank", "unknown") else []
            items = parse_items(line) if step_type in ("item_action", "bank", "unknown") else []
            quest = parse_quest_tag(line)
            instruction = CLEAN_RE.sub("", line).strip("* ").strip()
            name = instruction[:50].replace(" ", "_").lower() or f"step{lineno}"
            panel_name = quest or current_panel
            out.append({
                "lineno": lineno,
                "raw": line,
                "type": step_type,
                "npc_names": npc_names,
                "object_names": object_names,
                "items": items,
                "dialogue_options": dialogue,
                "quest_tag": quest,
                "panel_name": panel_name,
                "instruction": instruction,
                "name": name
            })
    with open(args.outfile, "w", encoding="utf-8") as w:
        json.dump(out, w, ensure_ascii=False, indent=2)
    print(f"Wrote {len(out)} steps to {args.outfile}")

if __name__ == "__main__":
    main()