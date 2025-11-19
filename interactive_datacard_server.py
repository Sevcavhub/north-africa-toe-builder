#!/usr/bin/env python3
"""
Interactive Datacard Builder - Flask Web Server

Serves the interactive HTML interface and provides API endpoints
for building datacards with custom vehicle selections.

Usage:
    python interactive_datacard_server.py

Then open: http://localhost:5000
"""

from flask import Flask, jsonify, request, send_file, send_from_directory
from flask_cors import CORS
import sqlite3
import sys
from pathlib import Path
import json
from datetime import datetime

# Add project root to path
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

from scripts.battlegroup.book.generate_book_datacards_v6 import BookDatacardGenerator

app = Flask(__name__)
CORS(app)  # Enable CORS for local development

DATABASE_PATH = project_root / "database" / "master_database.db"
OUTPUT_DIR = project_root / "interactive_outputs"
OUTPUT_DIR.mkdir(exist_ok=True)


@app.route('/')
def index():
    """Serve the interactive HTML interface."""
    return send_from_directory('.', 'interactive_datacard_builder.html')


@app.route('/api/vehicles')
def get_vehicles():
    """Get list of all available vehicles from database."""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT name
            FROM bg_builder_vehicles
            ORDER BY name
        """)

        vehicles = [row[0] for row in cursor.fetchall()]
        conn.close()

        return jsonify(vehicles)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/build-datacards', methods=['POST'])
def build_datacards():
    """
    Build datacards from selected vehicles.

    Request body:
    {
        "vehicles": [
            {"name": "Panzer III H", "nation": "german"},
            {"name": "M4 Sherman (A1,A2,A3)", "nation": "british"}
        ]
    }
    """
    try:
        data = request.get_json()
        vehicles = data.get('vehicles', [])

        if not vehicles:
            return jsonify({"error": "No vehicles selected"}), 400

        # Generate datacards
        conn = sqlite3.connect(DATABASE_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        generator = BookDatacardGenerator()

        # Build equipment list
        equipment_list = []
        for vehicle in vehicles:
            vehicle_name = vehicle['name']
            nation = vehicle.get('nation', 'auto')

            # Look up vehicle ID
            cursor.execute("""
                SELECT id, name
                FROM bg_builder_vehicles
                WHERE name = ?
            """, (vehicle_name,))

            row = cursor.fetchone()
            if row:
                equipment_dict = {
                    'bg_builder_vehicle_id': row['id'],
                    'name': row['name'],
                    'equipment_type': 'vehicle',
                    'category': 'armored_vehicle'
                }

                # Add nation override if not auto
                if nation != 'auto':
                    equipment_dict['nation_override'] = nation

                equipment_list.append(equipment_dict)

        # Generate HTML output
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = OUTPUT_DIR / f"datacards_{timestamp}.html"

        with open(output_file, 'w', encoding='utf-8') as f:
            # Write HTML header
            f.write("<!DOCTYPE html>\n<html>\n<head>\n")
            f.write("<meta charset='UTF-8'>\n")
            f.write(f"<title>Custom Datacards - {timestamp}</title>\n")

            # Extract CSS from generator
            import re
            gen_path = project_root / "scripts" / "battlegroup" / "book" / "generate_book_datacards_v6.py"
            with open(gen_path, 'r', encoding='utf-8') as gen_file:
                gen_content = gen_file.read()
                css_match = re.search(r'css = """(.*?)"""', gen_content, re.DOTALL)
                if css_match:
                    css = css_match.group(1)
                    if '\n---\n' in css:
                        css = css.split('\n---\n')[0]
                    f.write(css)

            # Close head, open body
            f.write("</head>\n<body>\n")
            f.write(f"<h1 style='text-align:center; padding:20px;'>Custom Datacards - {len(equipment_list)} vehicles</h1>\n")
            f.write('<div class="datacard-grid">\n\n')

            # Generate datacards
            for equipment in equipment_list:
                datacard = generator.generate_datacard_markdown(equipment, 'r')
                f.write(datacard)
                f.write('\n')

            # Close HTML
            f.write("</div>\n")
            f.write("</body>\n</html>\n")

        generator.close()
        conn.close()

        return jsonify({
            "success": True,
            "message": f"Generated {len(equipment_list)} datacards",
            "download_url": f"/download/{output_file.name}",
            "vehicle_count": len(equipment_list)
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route('/api/build-datacards-html', methods=['POST'])
def build_datacards_html():
    """
    Build datacards and return HTML directly (for opening in new tab).

    Request body:
    {
        "vehicles": [
            {"name": "Panzer III H", "nation": "german"},
            {"name": "M4 Sherman (A1,A2,A3)", "nation": "british"}
        ]
    }

    Returns: HTML content directly
    """
    try:
        data = request.get_json()
        vehicles = data.get('vehicles', [])

        if not vehicles:
            return "<html><body><h1>Error: No vehicles selected</h1></body></html>", 400

        # Generate datacards
        conn = sqlite3.connect(DATABASE_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        generator = BookDatacardGenerator()

        # Build equipment list
        equipment_list = []
        for vehicle in vehicles:
            vehicle_name = vehicle['name']
            nation = vehicle.get('nation', 'auto')

            # Look up vehicle ID
            cursor.execute("""
                SELECT id, name
                FROM bg_builder_vehicles
                WHERE name = ?
            """, (vehicle_name,))

            row = cursor.fetchone()
            if row:
                equipment_dict = {
                    'bg_builder_vehicle_id': row['id'],
                    'name': row['name'],
                    'equipment_type': 'vehicle',
                    'category': 'armored_vehicle'
                }

                # Add nation override if not auto
                if nation != 'auto':
                    equipment_dict['nation_override'] = nation

                equipment_list.append(equipment_dict)

        # Build HTML in memory
        html_parts = []
        html_parts.append("<!DOCTYPE html>\n<html>\n<head>\n")
        html_parts.append("<meta charset='UTF-8'>\n")
        html_parts.append(f"<title>Custom Datacards - {len(equipment_list)} vehicles</title>\n")

        # Extract CSS from generator
        import re
        gen_path = project_root / "scripts" / "battlegroup" / "book" / "generate_book_datacards_v6.py"
        with open(gen_path, 'r', encoding='utf-8') as gen_file:
            gen_content = gen_file.read()
            css_match = re.search(r'css = """(.*?)"""', gen_content, re.DOTALL)
            if css_match:
                css = css_match.group(1)
                if '\n---\n' in css:
                    css = css.split('\n---\n')[0]
                html_parts.append(css)

        # Close head, open body
        html_parts.append("</head>\n<body>\n")
        html_parts.append(f"<h1 style='text-align:center; padding:20px;'>Custom Datacards - {len(equipment_list)} vehicles</h1>\n")
        html_parts.append('<div class="datacard-grid">\n\n')

        # Generate datacards
        for equipment in equipment_list:
            datacard = generator.generate_datacard_markdown(equipment, 'r')
            html_parts.append(datacard)
            html_parts.append('\n')

        # Close HTML
        html_parts.append("</div>\n")
        html_parts.append("</body>\n</html>\n")

        generator.close()
        conn.close()

        # Return HTML directly
        return ''.join(html_parts), 200, {'Content-Type': 'text/html; charset=utf-8'}

    except Exception as e:
        import traceback
        traceback.print_exc()
        return f"<html><body><h1>Error</h1><pre>{str(e)}</pre></body></html>", 500


@app.route('/download/<filename>')
def download_file(filename):
    """Download generated datacard HTML file."""
    try:
        return send_file(
            OUTPUT_DIR / filename,
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 404


if __name__ == '__main__':
    print("\n" + "="*70)
    print("Interactive Datacard Builder Server")
    print("="*70)
    print(f"\nOutput directory: {OUTPUT_DIR}")
    print(f"Database: {DATABASE_PATH}")
    print("\nServer starting at: http://localhost:5000")
    print("\nOpen your browser and navigate to: http://localhost:5000")
    print("\nPress Ctrl+C to stop the server\n")

    app.run(debug=True, host='0.0.0.0', port=5000)
