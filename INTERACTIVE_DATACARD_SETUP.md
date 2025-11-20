# Interactive Datacard Builder - Setup Guide

## 📋 What Is This?

The Interactive Datacard Builder is a web-based tool for generating BattleGroup V6.1 datacards from our database of 602+ WWII vehicles and weapons.

**Features:**
- Search and select vehicles by name
- Override nation colors (German, British, Italian, American, French)
- Generate V6.1 datacards with weapon fallback support
- Auto-download HTML files for printing

## 🔧 Prerequisites

### Required Software:
1. **Python 3.8+** - Download from https://www.python.org/downloads/
   - During installation, check "Add Python to PATH"

2. **Required Python Packages:**
   ```bash
   pip install flask flask-cors
   ```

### Required Files:
You need the following from the project:
- `interactive_datacard_server.py` - Flask web server
- `interactive_datacard_builder.html` - Web interface
- `scripts/battlegroup/book/generate_book_datacards_v6_1.py` - V6.1 generator
- `database/master_database.db` - Equipment database (602 vehicles, 239 weapons)

## 🚀 Quick Start (Windows)

### Method 1: Batch File (Easiest)
1. Double-click `START_DATACARD_BUILDER.bat`
2. Wait for "Running on http://127.0.0.1:5000" message
3. Open your browser to http://localhost:5000
4. Press `Ctrl+C` in the terminal window to stop

### Method 2: Command Line
1. Open Command Prompt or PowerShell
2. Navigate to project directory:
   ```bash
   cd D:\north-africa-toe-builder
   ```
3. Run the server:
   ```bash
   python interactive_datacard_server.py
   ```
4. Open browser to http://localhost:5000
5. Press `Ctrl+C` to stop

## 🚀 Quick Start (Mac/Linux)

1. Open Terminal
2. Navigate to project directory:
   ```bash
   cd /path/to/north-africa-toe-builder
   ```
3. Run the server:
   ```bash
   python3 interactive_datacard_server.py
   ```
4. Open browser to http://localhost:5000
5. Press `Ctrl+C` to stop

## 📦 Sharing with a Colleague

### Option 1: Share Entire Project (Recommended)
**What to share:**
- Entire `north-africa-toe-builder` folder (includes all dependencies)

**Setup for colleague:**
1. Install Python 3.8+ (add to PATH)
2. Install packages: `pip install flask flask-cors`
3. Extract project folder to their computer
4. Run `START_DATACARD_BUILDER.bat` (Windows) or `python interactive_datacard_server.py` (Mac/Linux)

### Option 2: Share Minimal Package
**Required files only:**
```
north-africa-toe-builder/
├── interactive_datacard_server.py
├── interactive_datacard_builder.html
├── START_DATACARD_BUILDER.bat
├── database/
│   └── master_database.db
└── scripts/
    └── battlegroup/
        └── book/
            └── generate_book_datacards_v6_1.py
```

**Setup for colleague:**
1. Install Python 3.8+ and packages (see above)
2. Extract files maintaining folder structure
3. Run server

### Option 3: Cloud Deployment (Already Done!)
**No setup needed - just share the URL:**
- https://sevcavhub.github.io/north-africa-toe-builder/tools.html

This uses the Render.com API (https://north-africa-toe-api.onrender.com)

## 🎯 Using the Tool

### Basic Workflow:
1. Start the server (see Quick Start above)
2. Open http://localhost:5000 in browser
3. Search for vehicles (e.g., "Sherman", "Panzer III")
4. Click checkboxes to select vehicles
5. (Optional) Override nation for each vehicle
6. Click "Build Datacards"
7. HTML file downloads automatically

### Example Selections:
- **German Tank Company**: Panzer III G, Panzer IV F2, SdKfz 251/1
- **British Armored Squadron**: Crusader III, M4 Sherman, M3 Grant
- **American Armored Platoon**: M4A3E2 Sherman Jumbo, M10 Wolverine, M8 Greyhound

## 🔍 Troubleshooting

### "Unable to connect" error:
- Check server is running (terminal should show "Running on http://127.0.0.1:5000")
- Try http://127.0.0.1:5000 instead of http://localhost:5000
- Check port 5000 isn't used by another program

### "ModuleNotFoundError: No module named 'flask'":
- Install Flask: `pip install flask flask-cors`

### "Database not found" error:
- Ensure `database/master_database.db` exists
- Check file path in `interactive_datacard_server.py` (line ~35)

### "Vehicle not found" error:
- Check spelling (case-insensitive search works)
- Try partial names (e.g., "Jumbo" finds "M4A3E2 Sherman Jumbo")
- View full list at: http://localhost:5000/api/vehicles

### Port already in use:
- Stop other servers using port 5000
- Or edit `interactive_datacard_server.py` line at bottom:
  ```python
  app.run(host='0.0.0.0', port=5001, debug=True)  # Change to 5001
  ```

## 📊 Database Coverage

**Current Database (November 2025):**
- 602 vehicles in `bg_builder_vehicles`
- 239 weapons in `bg_builder_weapons`
- 119 manually extracted vehicles in `bg_reference_vehicles`
- V6.1 weapon fallback: Uses builder data when manual extraction unavailable

**Nations Covered:**
- German (Panzer I-VI, SdKfz, Sturmgeschütz)
- British (Matilda, Crusader, Valentine, Sherman, Grant)
- Italian (L3, L6, M13/40, Semovente)
- American (M3 Stuart, M4 Sherman, M10, M8)
- French (Char B1, Somua S35, Hotchkiss H39)

## 🆘 Support

### Check Server Status:
Visit http://localhost:5000/api/vehicles to see JSON list of all vehicles.

### View Server Logs:
The terminal window shows all requests and errors in real-time.

### Common Issues:
1. **No weapons showing**: V6.1 fallback handles this automatically
2. **Wrong nation colors**: Use nation override dropdown
3. **Slow generation**: Normal for 10+ vehicles (allows up to 2 minutes)

## 🔗 Related Tools

### OSJones Builder Integration:
1. Go to https://osjones.github.io/BattlegroupBuilder/
2. Build army list
3. Click "Print" and copy output (Ctrl+A, Ctrl+C)
4. Paste into tools page: https://sevcavhub.github.io/north-africa-toe-builder/tools.html
5. Click "Generate Datacards"

### Command Line Alternative:
```bash
# Generate datacards from equipment list
python scripts/battlegroup/book/generate_datacards_from_army_list_v6.py \
  --equipment "Panzer III,Panzer IV,88mm FlaK" \
  --output datacards/
```

## 📝 Version History

**V6.1** (November 2025):
- Added weapon fallback system
- Sherman Jumbo and 480+ additional vehicles now supported
- Non-breaking: Manual extraction still prioritized

**V6.0** (November 2025):
- Changed lookup from canonical_id to bg_builder_vehicles.name
- Simplified equipment workflow

**V5.5** (November 2025):
- Added silhouette images
- Nation-specific color themes

## 📄 License

This tool is part of the North Africa TO&E Builder project.
For internal use and wargaming scenario generation.

## 🤝 Contributing

Found a bug or have a suggestion? Contact the project maintainer.

Database improvements needed:
- Ammunition capacity data (Jane's guide parsing)
- Additional vehicle variants
- Special rules validation
