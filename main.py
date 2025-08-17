import html
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Optional, Tuple

import requests

URL = (
    "https://oldschool.runescape.wiki/w/Guide:"
    "B0aty_HCIM_Guide_V3?action=edit"
)
OUTPUT_FILE = "wiki.txt"

FOLLOW_UP_SCRIPTS = [
    "cleanwiki.py",
    "worldpointscraper.py",
    "cleanQHDatabase.py",
    "run_all.py",
]


def prompt_range() -> Tuple[Optional[int], Optional[int]]:
    patt = re.compile(r"^(\d+)-(\d+)$")

    while True:
        ans = input("Enter Bank range (all or N-M, e.g. 1-10): ").strip().lower()
        if ans == "all":
            return None, None

        m = patt.fullmatch(ans)
        if m:
            lo, hi = map(int, m.groups())
            if lo <= hi:
                return lo, hi

        print("  Invalid input. Use 'all' or N-M with N ≤ M (example: 3-8).")


def fetch_wikitext(url: str) -> str:
    page = requests.get(url, timeout=30)
    page.raise_for_status()

    match = re.search(r"<textarea[^>]*>(.*?)</textarea>", page.text, re.DOTALL)
    if not match:
        raise RuntimeError("Could not locate <textarea> with wikitext.")

    return html.unescape(match.group(1))


BANK_COMMENT_RE = re.compile(r"<!--\s*Bank\s*(\d+)\s*-->", re.IGNORECASE)


def strip_trailing_braces(lines: list[str]) -> list[str]:
    while lines and lines[-1].strip() == "}}":
        lines.pop()
    return lines


def keep_block(bank_no: int, lo: Optional[int], hi: Optional[int]) -> bool:
    if lo is None or hi is None:  # user typed 'all'
        return True
    return lo <= bank_no <= hi


def extract_bank_blocks(text: str, lo: Optional[int], hi: Optional[int]) -> list[str]:

    lines = text.splitlines()

    try:
        start = lines.index("{{DISPLAYTITLE:Guide:B0aty HCIM Guide V3}}")
    except ValueError:
        raise RuntimeError("DISPLAYTITLE line not found.")
    lines = lines[start:]

    out: list[str] = []
    i, n = 0, len(lines)

    while i < n:
        if lines[i].lstrip().startswith("{{Var"):
            block: list[str] = [lines[i]]
            i += 1
            while i < n and not lines[i].lstrip().startswith("{{Var"):
                block.append(lines[i])
                i += 1

            bank_no = None
            for ln in block:
                m = BANK_COMMENT_RE.search(ln)
                if m:
                    bank_no = int(m.group(1))
                    break

            if bank_no is not None and keep_block(bank_no, lo, hi):
                out.extend(strip_trailing_braces(block))
        else:
            out.append(lines[i])
            i += 1

    if not out or out[-1].strip() != "}}":
        out.append("}}")

    return out


def run_follow_up_scripts(script_dir: Path) -> None:

    python_exe = sys.executable

    for script_name in FOLLOW_UP_SCRIPTS:
        script_path = script_dir / script_name
        if not script_path.is_file():
            print(f"[WARN] {script_name} not found; skipping.")
            continue

        print(f"[INFO] Running {script_name} …")
        subprocess.run(
            [python_exe, str(script_path)],
            cwd=script_dir,
            check=True,
        )


def main() -> None:
    lo, hi = prompt_range()

    try:
        raw = fetch_wikitext(URL)
        lines = extract_bank_blocks(raw, lo, hi)
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"[INFO] Saved selected Bank sections to '{OUTPUT_FILE}'.\n")

    here = Path(__file__).resolve().parent
    try:
        run_follow_up_scripts(here)
    except subprocess.CalledProcessError as exc:
        print(f"[ERROR] {exc} (exit code {exc.returncode})", file=sys.stderr)
        sys.exit(exc.returncode)

    print("\n[INFO] All helper scripts completed successfully.")


if __name__ == "__main__":
    main()