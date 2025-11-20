# 🎯 Interactive Datacard Builder v6

**A classy web-based interface for building custom BattleGroup datacards**

![Interactive Builder](https://img.shields.io/badge/Version-6.0-blue) ![Status](https://img.shields.io/badge/Status-Ready-green)

## 🌟 Features

- **Interactive Web Interface** - Beautiful, modern UI with dropdown selections
- **602 Vehicles Available** - Full access to bg_builder_vehicles database
- **Nation Override** - Choose which nation uses each vehicle (e.g., Sherman used by British)
- **Live Preview** - See your selection list update in real-time
- **One-Click Generation** - Build datacards instantly with the click of a button
- **Auto-Download** - Generated HTML files automatically download to your browser

## 🚀 Quick Start

### Step 1: Start the Server

```bash
cd D:\north-africa-toe-builder
python interactive_datacard_server.py
```

You should see:
```
🎯 Interactive Datacard Builder Server
======================================================================

📂 Output directory: D:\north-africa-toe-builder\interactive_outputs
📊 Database: D:\north-africa-toe-builder\database\master_database.db

🌐 Server starting at: http://localhost:5000

Open your browser and navigate to: http://localhost:5000
```

### Step 2: Open Your Browser

Navigate to: **http://localhost:5000**

### Step 3: Build Your Datacards

1. **Search** for a vehicle in the search box (e.g., "Sherman")
2. **Select** the vehicle from the dropdown
3. **Choose** a nation:
   - **Auto-detect** - Use database default (recommended)
   - **🇬🇧 British** - Tan/beige cards
   - **🇩🇪 German** - Gray cards
   - **🇮🇹 Italian** - Green cards
   - **🇺🇸 American** - Olive cards
   - **🇫🇷 French** - Blue cards
4. Click **➕ Add to List**
5. Repeat for all desired vehicles
6. Click **🚀 Build Datacards** when ready
7. **Download automatically starts** - Open the HTML file in your browser

## 📋 Example Use Case

**Scenario**: You want datacards for a mixed British force using captured/lend-lease equipment

1. Add `Matilda II` (Auto-detect → British)
2. Add `Crusader III` (Auto-detect → British)
3. Add `M4 Sherman (A1,A2,A3)` with Nation: **British** (override American default)
4. Add `Panzer IV F2` with Nation: **British** (captured German tank)
5. Click Build Datacards
6. Get a single HTML with 4 vehicles, all styled as British

## 🎨 Interface Features

### Left Panel: Add Vehicle
- **Search Box** - Type-to-filter search (e.g., "Panzer")
- **Vehicle Dropdown** - Scrollable list of all 602 vehicles
- **Nation Selector** - Override nation or use auto-detect
- **Add Button** - Add to your selection list

### Right Panel: Selected Vehicles
- **Live Counter** - Shows total vehicles selected
- **Vehicle List** - Visual cards showing name + nation
- **Remove Buttons** - Click ✕ to remove individual vehicles
- **Build Button** - Generate datacards (disabled until vehicles selected)
- **Status Messages** - Success/error feedback

## 📁 Output Files

Generated files are saved to: `D:\north-africa-toe-builder\interactive_outputs/`

**Filename format**: `datacards_YYYYMMDD_HHMMSS.html`

**Example**: `datacards_20251118_143022.html`

Each file contains:
- All selected vehicles as datacards
- V5.5 format (nation colors, silhouettes, multi-row armament)
- Print-ready (Ctrl+P in browser for PDF)

## 🛠️ Technical Details

**Frontend**: Pure HTML/CSS/JavaScript
- No external dependencies
- Works in any modern browser
- Responsive design

**Backend**: Python Flask
- Serves HTML interface
- Provides `/api/vehicles` endpoint (vehicle list)
- Provides `/api/build-datacards` endpoint (generation)
- Uses `generate_book_datacards_v6.py` for datacard generation

**Database**: SQLite
- Reads from `bg_builder_vehicles` (602 vehicles)
- Reads from `bg_reference_vehicles` (nation/metadata)
- Reads from `bg_builder_vehicle_costs` (points/BR)
- Reads from `bg_builder_weapons` (HE/AP values)

## 🔧 Troubleshooting

### Server won't start
**Error**: `ModuleNotFoundError: No module named 'flask'`
**Fix**: Install Flask: `pip install flask flask-cors`

### No vehicles show up
**Error**: Dropdown shows "Loading vehicles..."
**Fix**: Check database path in `interactive_datacard_server.py` line 23

### Datacards generate but download fails
**Fix**: Check browser downloads folder, or try different browser

### Nation colors don't show
**Fix**: Ensure you selected a nation (not just auto-detect) if you want specific colors

## 📊 Vehicle Statistics

- **Total Vehicles**: 602 in bg_builder_vehicles
- **With Nation Data**: ~500 in bg_reference_vehicles
- **With Costs**: 119 in bg_builder_vehicle_costs
- **With Weapons**: 239 weapons in bg_builder_weapons

## 🎯 Comparison: Interactive vs Script

| Feature | Interactive Builder | SAMPLE_DATACARDS_V6.py |
|---------|-------------------|------------------------|
| **Ease of Use** | ⭐⭐⭐⭐⭐ Click & select | ⭐⭐⭐ Edit Python code |
| **Search** | ✅ Type-to-filter | ❌ Manual lookup |
| **Nation Override** | ✅ Dropdown per vehicle | ✅ Dict format |
| **Preview** | ✅ Live vehicle list | ❌ None |
| **Speed** | ⭐⭐⭐⭐ Instant | ⭐⭐⭐⭐⭐ Fastest |
| **Output** | Auto-download HTML | File in project root |

**Recommendation**: Use **Interactive Builder** for custom one-off builds, use **Python script** for repeated/automated builds

## 🚀 Advanced Usage

### Custom Backend Port

Edit `interactive_datacard_server.py` line 243:

```python
app.run(debug=True, host='0.0.0.0', port=8080)  # Change to 8080
```

### Add More Nations

Edit `interactive_datacard_builder.html` lines 95-101 to add more nation options.

### Batch Export

Use the Python API directly:

```python
import requests

vehicles = [
    {"name": "Panzer III H", "nation": "german"},
    {"name": "M4 Sherman (A1,A2,A3)", "nation": "british"}
]

response = requests.post('http://localhost:5000/api/build-datacards', json={'vehicles': vehicles})
print(response.json())
```

## 📝 Credits

- **Generator**: `generate_book_datacards_v6.py`
- **Database**: OSJones Builder data (bg_builder_* tables)
- **Format**: BattleGroup V5.5 datacard specification
- **UI Design**: Modern gradient card interface

---

**Enjoy building your custom datacards!** 🎲
