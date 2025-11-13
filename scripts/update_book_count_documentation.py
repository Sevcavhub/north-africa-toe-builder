"""
Update documentation files to reflect 12 books instead of 4.

Updates CLAUDE.md, PROJECT_SCOPE.md, PHASE_9B_NEXT_STEPS.md, and PHASE_9B_SESSION_SUMMARY.md
to correctly reference the 12 BattleGroup books being generated.
"""

from pathlib import Path

# Project root
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent

# Files to update
FILES_TO_UPDATE = [
    Path("D:/north-africa-toe-builder/CLAUDE.md"),
    Path("D:/north-africa-toe-builder/PROJECT_SCOPE.md"),
    Path("D:/north-africa-toe-builder/PHASE_9B_NEXT_STEPS.md"),
    Path("D:/north-africa-toe-builder/PHASE_9B_SESSION_SUMMARY.md")
]

# Replacements to make
REPLACEMENTS = [
    # General references to 4 books
    ("4 books", "12 books"),
    ("4 battle books", "12 battle books"),
    ("all 4 books", "all 12 books"),
    ("4 beautiful books", "12 beautiful books"),
    ("4 professional-quality books", "12 professional-quality books"),
    ("4 complete books", "12 complete books"),

    # Specific book lists
    (
        "4 beautiful books: Operation Battleaxe, Operation Crusader, Battle of Gazala, First El Alamein",
        "12 comprehensive battle books covering the entire North Africa campaign (1940-1943)"
    ),
    (
        "4 books: Operation Battleaxe, Operation Crusader, Battle of Gazala, First El Alamein",
        "12 books: Compass, Sonnenblume, Battleaxe, Crusader, Gazala, Tobruk, First Alamein, Alam Halfa, Second Alamein, Torch, Tunisia, Mareth"
    ),
    (
        "- Operation Battleaxe (1941-Q2)\n- Operation Crusader (1941-Q4)\n- Battle of Gazala (1942-Q2)\n- First El Alamein (1942-Q3)",
        "- Compass (1940-Q4), Sonnenblume (1941-Q1), Battleaxe (1941-Q2)\n- Crusader (1941-Q4), Gazala (1942-Q2), Tobruk (1942-Q2)\n- First Alamein (1942-Q3), Alam Halfa (1942-Q3), Second Alamein (1942-Q4)\n- Torch (1942-Q4), Tunisia (1943-Q1), Mareth (1943-Q1)"
    ),
]

def update_file(file_path: Path) -> tuple[bool, int]:
    """
    Update a single documentation file.

    Returns:
        (modified: bool, replacements_made: int)
    """
    if not file_path.exists():
        print(f"  [SKIP] File not found: {file_path.name}")
        return False, 0

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content
    replacements_made = 0

    for old, new in REPLACEMENTS:
        if old in content:
            content = content.replace(old, new)
            replacements_made += content.count(new) - original_content.count(new)

    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True, replacements_made

    return False, 0

def main():
    """Update all documentation files."""
    print("Updating documentation to reflect 12 books (not 4)...\n")

    total_modified = 0
    total_replacements = 0

    for file_path in FILES_TO_UPDATE:
        print(f"Processing: {file_path.name}")
        modified, replacements = update_file(file_path)

        if modified:
            print(f"  [UPDATED] {replacements} replacements made")
            total_modified += 1
            total_replacements += replacements
        else:
            if file_path.exists():
                print(f"  [NO CHANGES] File already correct or no matches found")

    print(f"\n{'='*60}")
    print(f"SUMMARY")
    print(f"{'='*60}")
    print(f"Files modified: {total_modified}/{len(FILES_TO_UPDATE)}")
    print(f"Total replacements: {total_replacements}")
    print(f"{'='*60}")

if __name__ == '__main__':
    main()
