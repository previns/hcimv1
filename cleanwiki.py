import re
from pathlib import Path

def clean_wiki_file(input_file: str, output_file: str) -> None:
    """Clean wiki markup from v3.txt and extract checklist steps with bullet points."""
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: {input_file} not found.")
        return
    except Exception as e:
        print(f"Error reading {input_file}: {e}")
        return

    # Split content into lines
    lines = content.splitlines()
    cleaned_lines = []
    in_checklist = False
    current_title = None
    bank_number = 0  # Start at 0, update from titles or {{Var}}
    checklist_pattern = re.compile(r'\{\{Checklist\|title=([^|]+)\|')
    var_pattern = re.compile(r'\{\{Var\| bankNumber \| \{{#expr:\{{#var:bankNumber}}\+1}}\}\}')
    expr_pattern = re.compile(r'Bank \{{#expr:\{{#var:bankNumber}}\+1}}([AB]?)')
    bank_number_pattern = re.compile(r'Bank (\d+[AB]?)')
    item_pattern = re.compile(r'(\*+\s*.*?)(?=\n|$)', re.DOTALL)
    comment_pattern = re.compile(r'<!--\s*(?:Bank\s*)?(\d+[AB]?)\s*-->')
    skip_patterns = [
        r'\{\{Youtube\|.*?\}\}',  # Remove {{Youtube}}
        r'\{\{Extimage\|.*?\}\}',  # Remove {{Extimage}}
        r'==.*?=='                # Remove headers
    ]

    def normalize_bank_label(label: str) -> str:
        """Only ensure 'Bank ' prefix for numeric or alphanumeric bank labels."""
        # If it starts with 'Bank ' already, leave it
        if label.lower().startswith("bank "):
            return label
        # Add 'Bank ' only if label starts with a digit (e.g., '39', '39A', '40B')
        if re.match(r'^\d+[A-Z]?$' , label, re.IGNORECASE):
            return f"Bank {label}"
        return label
    
    for line in lines:
        line = line.strip()
        # Skip empty lines and unwanted wiki markup
        if not line or any(re.match(pattern, line) for pattern in skip_patterns):
            continue

        # Increment bankNumber on {{Var|bankNumber|{{#expr:{{#var:bankNumber}}+1}}}}
        var_match = var_pattern.match(line)
        if var_match:
            bank_number += 1
            continue

        # Handle explicit comments
        comment_match = comment_pattern.match(line)
        if comment_match:
            comment_bank = comment_match.group(1)
            # Skip pure numeric (e.g., "1") but keep things like "39A"
            if comment_bank.isdigit():
                continue
            label = normalize_bank_label(comment_bank)
            # Avoid duplicates like ### 39A / ### Bank 39A
            if cleaned_lines and cleaned_lines[-1] == f"### {label}":
                continue
            cleaned_lines.append(f"### {label}")
            current_title = label  # Track so we can skip matching checklist title
            continue

        # Detect checklist start and resolve title
        checklist_match = checklist_pattern.match(line)
        if checklist_match:
            in_checklist = True
            raw_title = checklist_match.group(1).strip()
            # Skip pure numeric titles (e.g., "1")
            if raw_title.isdigit():
                continue
            # Resolve expr pattern only if it doesn't duplicate the last comment
            expr_match = expr_pattern.match(raw_title)
            if expr_match:
                suffix = expr_match.group(1)
                proposed_title = f"Bank {bank_number + 1}{suffix}"
                if current_title == proposed_title:
                    # Skip because comment already handled it
                    continue
                raw_title = proposed_title
            # Update bank_number from explicit titles (e.g., "Bank 1")
            bank_number_match = bank_number_pattern.match(raw_title)
            if bank_number_match:
                try:
                    num_part = re.match(r'\d+', bank_number_match.group(1)).group()
                    bank_number = max(bank_number, int(num_part))
                except ValueError:
                    pass
            raw_title = normalize_bank_label(raw_title)
            # Avoid duplicate consecutive headings
            if cleaned_lines and cleaned_lines[-1] == f"### {raw_title}":
                continue
            cleaned_lines.append(f"### {raw_title}")
            current_title = raw_title
            continue

        # Extract checklist items with bullet points
        if in_checklist and line.startswith('*'):
            item_match = item_pattern.match(line)
            if item_match:
                cleaned_lines.append(item_match.group(1).strip())
            continue

        # End checklist when encountering a new section or end of checklist
        if in_checklist and (line.startswith('{{') or line.startswith('}')):
            in_checklist = False
            current_title = None
            continue

    # Write cleaned output
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(cleaned_lines) + '\n')
        print(f"Cleaned file saved successfully at {output_file}")
    except Exception as e:
        print(f"Error writing {output_file}: {e}")

def main():
    """Main function to clean v3.txt."""
    script_dir = Path(__file__).parent
    input_file = script_dir / "wiki.txt"
    output_file = script_dir / "wiki_cleaned.txt"
    clean_wiki_file(input_file, output_file)

if __name__ == "__main__":
    main()
