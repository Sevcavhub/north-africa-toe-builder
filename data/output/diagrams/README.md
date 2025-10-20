# TO&E Organizational Diagrams

This directory contains organizational diagrams for military units showing hierarchical structure and equipment allocations.

## Sample: 7th Armoured Division (Desert Rats) - June 1942

### Files Created

1. **`7th_armoured_division_1942_mermaid.md`**
   - Mermaid diagram (text-based)
   - Works in MDBook without additional software
   - No tank silhouettes (text labels only)

2. **`7th_armoured_division_1942.dot`**
   - Graphviz DOT file (with tank silhouette images)
   - Requires Graphviz to render
   - Professional-quality output

## Viewing the Mermaid Diagram

**Option 1: MDBook (Recommended for books)**
1. Copy the code block from `7th_armoured_division_1942_mermaid.md`
2. Paste into any MDBook markdown file
3. MDBook will auto-render the diagram

**Option 2: VS Code Extension**
1. Install "Markdown Preview Mermaid Support" extension
2. Open `7th_armoured_division_1942_mermaid.md`
3. Preview with Ctrl+Shift+V

**Option 3: Mermaid Live Editor**
1. Visit: https://mermaid.live/
2. Copy the mermaid code block
3. Paste and view rendered diagram

## Rendering the Graphviz Diagram

### Install Graphviz (Required)

**Windows:**
1. Download: https://graphviz.org/download/#windows
2. Run installer (choose "Add to PATH" option)
3. Verify: Open new terminal, run `dot -V`

**Or via Chocolatey:**
```bash
choco install graphviz
```

### Render to PNG

```bash
cd data/output/diagrams
dot -Tpng 7th_armoured_division_1942.dot -o 7th_armoured_division_1942.png
```

### Render to SVG (Scalable)

```bash
dot -Tsvg 7th_armoured_division_1942.dot -o 7th_armoured_division_1942.svg
```

### Render to PDF

```bash
dot -Tpdf 7th_armoured_division_1942.dot -o 7th_armoured_division_1942.pdf
```

## Tank Silhouettes

**Current Status:**
- ✅ Simple placeholder SVGs created in `data/assets/tank_silhouettes/british/`
  - `crusader_mk3.svg` (placeholder)
  - `m3_grant.svg` (placeholder)
  - `m3_stuart.svg` (placeholder)

**Upgrade to Professional Silhouettes:**

See: `data/assets/tank_silhouettes/README.md` for:
- Wikimedia Commons sources (public domain)
- OnWar.com technical drawings
- Naming conventions
- Image specifications

## Generating Diagrams from Unit JSON

### Manual Process (Current)

1. Read unit JSON file (e.g., `data/output/units/british_1942q2_7th_armoured_division_toe.json`)
2. Extract organizational hierarchy and equipment
3. Create DOT file following the template in `7th_armoured_division_1942.dot`
4. Render with Graphviz

### Automated Script (To Be Created)

```bash
# Future implementation
node scripts/generate_org_diagram.js \
  --unit data/output/units/british_1942q2_7th_armoured_division_toe.json \
  --format graphviz \
  --output data/output/diagrams/
```

## Use Cases

### MDBook Chapters
- Use Mermaid for simple organizational charts
- Shows command hierarchy clearly
- No external dependencies

### WITW Scenarios
- Use Graphviz with tank silhouettes
- Professional reference diagrams
- Include in scenario documentation

### Presentations/Reports
- Render Graphviz to SVG for embedding
- Scalable, high-quality output
- Print-ready diagrams

## Example Output

**Mermaid** (in MDBook):
- Colored boxes showing division → brigade → regiment
- Text labels for equipment counts
- Clean, professional look

**Graphviz** (rendered):
- Tank silhouettes showing actual vehicle types
- Hierarchical layout with commander names
- Equipment breakdowns at each level
- Publication-quality graphics

## Next Steps

1. **Install Graphviz** (if rendering DOT files)
2. **Source better tank silhouettes** (see silhouettes/README.md)
3. **Create automation script** to generate diagrams from JSON
4. **Integrate with MDBook** generation workflow
